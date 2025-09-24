# ---- minimal invoice flow ----
import os, time, json, requests, logging
from myApp.models import Order, ProductComponent

log = logging.getLogger(__name__)

ZOHO_CLIENT_ID     = os.getenv("ZOHO_CLIENT_ID","")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET","")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN","")
ZOHO_ORG_ID        = os.getenv("ZOHO_ORG_ID","")
ZOHO_BASE          = (os.getenv("ZOHO_BASE","https://www.zohoapis.com") or "https://www.zohoapis.com").rstrip("/")

# --- token + http ---
def _accounts_from_base(b: str) -> str:
    b = (b or "").lower()
    if "zohoapis.eu" in b: return "https://accounts.zoho.eu"
    if "zohoapis.in" in b: return "https://accounts.zoho.in"
    return "https://accounts.zoho.com"

_TOK, _TOK_EXP = None, 0
def _get_access_token() -> str:
    global _TOK, _TOK_EXP
    now = time.time()
    if _TOK and now < _TOK_EXP - 60:
        return _TOK
    url = f"{_accounts_from_base(ZOHO_BASE)}/oauth/v2/token"
    data = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token",
    }
    r = requests.post(url, data=data, timeout=30)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Zoho token error {r.status_code}: {r.text[:600]}") from e
    js = r.json()
    _TOK = js["access_token"]
    _TOK_EXP = now + int(js.get("expires_in", 3600))
    return _TOK

def _api_url(p: str) -> str:
    return f"{ZOHO_BASE}/inventory/v1/{p.lstrip('/')}"

def _headers():
    return {
        "Authorization": f"Zoho-oauthtoken {_get_access_token()}",
        "X-com-zoho-inventory-organizationid": str(ZOHO_ORG_ID),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def _zget(path, params=None):
    url = _api_url(path)
    p = {"organization_id": ZOHO_ORG_ID}
    if params: p.update(params)
    r = requests.get(url, headers=_headers(), params=p, timeout=30)
    r.raise_for_status()
    return r.json()

def _zpost(path, payload):
    url = _api_url(path)
    r = requests.post(url, headers=_headers(), params={"organization_id": ZOHO_ORG_ID}, json=payload, timeout=30)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"POST {url} -> {r.status_code}: {r.text[:1000]}") from e
    return r.json()

# --- helpers ---
def _line_items(order: Order):
    """Expand bundles into components; resolve items by SKU."""
    out = []
    for line in order.items.select_related("product"):
        p = line.product
        if p.is_bundle:
            for link in p.component_rows():      # uses your Product.component_rows()
                c = link.component
                out.append({
                    "sku": c.sku or None,        # Zoho resolves item by SKU
                    "name": c.name,
                    "item_id": None,
                    "quantity": float(line.quantity * (link.quantity or 1)),
                    "rate": float(c.price),
                })
        else:
            out.append({
                "sku": p.sku or None,
                "name": p.name,
                "item_id": None,
                "quantity": float(line.quantity),
                "rate": float(line.unit_price),
            })
    return out

def _ensure_contact_id(order: Order) -> str:
    """Find/create a Zoho customer; store rich address on the *contact* only."""
    # 1) by email
    if order.email:
        try:
            res = _zget("contacts", params={"email": order.email})
            lst = res.get("contacts") or []
            if lst: return lst[0]["contact_id"]
        except Exception:
            pass
    # 2) by name
    try:
        res = _zget("contacts", params={"name": order.full_name})
        lst = res.get("contacts") or []
        if lst: return lst[0]["contact_id"]
    except Exception:
        pass
    # 3) create (keep addresses short so they always pass)
    a = order.shipping_address or {}
    def short(s, n): 
        s = (s or "").strip()
        return s[:n] if s else None
    contact_payload = {
        "contact_name": order.full_name or f"Guest {order.order_number}",
        "contact_type": "customer",
        "email": order.email or None,
        "phone": order.phone or None,
        "shipping_address": {
            "attention": short(order.full_name, 100),
            "address":  short(a.get("address_line1") or a.get("address") or order.shipping_address_text, 60),
            "city":     short(a.get("city") or a.get("area") or "", 60),
            "country":  short({"JO":"Jordan","AE":"United Arab Emirates","US":"United States","GB":"United Kingdom"}.get((order.country or "").upper(), order.country), 60),
        },
        "billing_address": {
            "attention": short(order.full_name, 100),
            "address":  short(a.get("address_line1") or a.get("address") or order.shipping_address_text, 60),
            "city":     short(a.get("city") or a.get("area") or "", 60),
            "country":  short({"JO":"Jordan","AE":"United Arab Emirates","US":"United States","GB":"United Kingdom"}.get((order.country or "").upper(), order.country), 60),
        },
    }
    res = _zpost("contacts", contact_payload)
    return (res.get("contact") or {}).get("contact_id")

# --- public: create invoice (deduct stock) ---
def create_invoice_for_order(order: Order) -> tuple[bool, str | dict]:
    """
    Creates a Zoho *Invoice* for the given order.
    - Deducts stock immediately.
    - Uses the Contact's saved address (we don't send long address fields here).
    Returns (ok, invoice_id or error_text).
    """
    try:
        cid = _ensure_contact_id(order)
        payload = {
            "customer_id": cid,
            "reference_number": order.order_number,
            "date": time.strftime("%Y-%m-%d"),
            "line_items": _line_items(order),
            # no shipping/billing address here → avoids 100-char traps
            "customer_notes": (order.shipping_address_text or "")[:200],
        }
        res = _zpost("invoices", payload)
        inv = res.get("invoice") or {}
        invoice_id = inv.get("invoice_id")
        log.info("Zoho invoice created: %s for order %s", invoice_id, order.order_number)
        return True, invoice_id or inv
    except Exception as e:
        log.exception("Zoho invoice create failed for %s", order.order_number)
        return False, str(e)
