# myApp/integrations/zoho_inventory.py
import os, time, json, requests, logging, re
from decimal import Decimal
from myApp.models import Order, Product, ProductComponent

log = logging.getLogger(__name__)

# ------------ Config ------------
DEBUG_ZOHO = True

AUTO_MARK_PAID       = True   # create Customer Payment after invoicing
PAYMENT_MODE_COD     = "Cash"
PAYMENT_MODE_ONLINE  = "Online"

# Show bundles as a single parent line (preferred). If True, explode into components.
EXPLODE_BUNDLES = False

ZOHO_CLIENT_ID     = os.getenv("ZOHO_CLIENT_ID", "")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN", "")
ZOHO_ORG_ID        = os.getenv("ZOHO_ORG_ID", "")
ZOHO_BASE          = (os.getenv("ZOHO_BASE", "https://www.zohoapis.com") or "https://www.zohoapis.com").rstrip("/")

# ------------ Token helpers ------------
def _accounts_from_base(api_base: str) -> str:
    base = (api_base or "").lower()
    if "zohoapis.eu" in base: return "https://accounts.zoho.eu"
    if "zohoapis.in" in base: return "https://accounts.zoho.in"
    return "https://accounts.zoho.com"

_TOK = None
_TOK_EXP = 0

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
        raise RuntimeError(f"Zoho token error {r.status_code}: {r.text[:800]}") from e
    js = r.json()
    _TOK = js["access_token"]
    _TOK_EXP = now + int(js.get("expires_in", 3600))
    return _TOK

# ------------ HTTP wrappers ------------
def _api_url(path: str) -> str:
    return f"{ZOHO_BASE}/inventory/v1/{path.lstrip('/')}"

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
    if DEBUG_ZOHO:
        print(f"🟢 POST {url}")
        try:
            print(json.dumps(payload, indent=2, ensure_ascii=False)[:1200])
        except Exception:
            print(str(payload)[:1200])
    r = requests.post(url, headers=_headers(), params={"organization_id": ZOHO_ORG_ID}, json=payload, timeout=30)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"POST {url} -> {r.status_code}: {r.text[:2000]}") from e
    return r.json()

def _zput(path, payload):
    url = _api_url(path)
    r = requests.put(url, headers=_headers(), params={"organization_id": ZOHO_ORG_ID}, json=payload, timeout=30)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"PUT {url} -> {r.status_code}: {r.text[:2000]}") from e
    return r.json()

# ------------ Helpers ------------
def _clip(s, n):
    if not s: return None
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s[:n]

def _clean(d: dict) -> dict:
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}

_COUNTRY_NAME = {"JO": "Jordan", "AE": "United Arab Emirates", "US": "United States", "GB": "United Kingdom"}

def _build_address(order: Order, *, include_phone: bool = False):
    a = order.shipping_address or {}
    line1  = a.get("address_line1") or order.shipping_address_text or ""
    city   = a.get("city") or a.get("area") or ""
    state  = a.get("state") or a.get("province") or ""
    zipc   = a.get("postal_code") or a.get("zip_code") or ""
    iso    = (order.country or "").strip().upper()
    country_name = _COUNTRY_NAME.get(iso, iso or None)
    def clean(s): return re.sub(r"\s+", " ", str(s)).strip() if s else None
    addr = clean(line1)
    if addr and len(addr) > 60: addr = addr[:60]
    out = {
        "attention": clean(order.full_name),
        "address": addr,
        "city": clean(city),
        "state": (clean(state)[:30] if state else None),
        "zip": (clean(zipc)[:20] if zipc else None),
        "country": country_name,
    }
    if include_phone and order.phone:
        out["phone"] = _clip(order.phone, 20)
    return _clean(out)

# ------------ Line items (bundle-aware) ------------
def _bundle_desc(p, qty) -> str:
    """Readable breakdown for bundle line description."""
    parts = []
    try:
        for link in ProductComponent.objects.filter(parent=p).select_related("component"):
            comp = link.component
            parts.append(f"{int(link.quantity or 1) * int(qty)}× {comp.name}")
    except Exception:
        return ""
    return "Includes: " + "; ".join(parts) if parts else ""

def _line_items(order: Order):
    """
    Build Zoho line_items.

    - EXPLODE_BUNDLES=False (default): keep bundle as one line (uses bundle SKU).
      Zoho will deduct component stock if the bundle SKU is a Composite Item in Zoho.
    - EXPLODE_BUNDLES=True: expand bundle into component lines.
    """
    out = []
    for line in order.items.select_related("product"):
        p = line.product
        qty = float(line.quantity)

        if getattr(p, "is_bundle", False):
            if EXPLODE_BUNDLES:
                # Legacy: explode bundle to components
                for link in ProductComponent.objects.filter(parent=p).select_related("component"):
                    c = link.component
                    out.append({
                        "sku": c.sku or None,
                        "name": c.name,
                        "item_id": None,
                        "quantity": float(line.quantity * (link.quantity or 1)),
                        "rate": float(c.price),  # note: component rate (ignores bundle pricing)
                    })
            else:
                # Preferred: send the bundle itself
                out.append({
                    "sku": p.sku or None,
                    "name": p.name,
                    "item_id": None,
                    "quantity": qty,
                    "rate": float(line.unit_price),       # bundle price from order line
                    "description": _bundle_desc(p, qty),  # human-friendly breakdown
                })
        else:
            out.append({
                "sku": p.sku or None,
                "name": p.name,
                "item_id": None,
                "quantity": qty,
                "rate": float(line.unit_price),
            })
    return out

# ------------ Contacts ------------
def _ensure_customer(order: Order):
    if order.email:
        try:
            res = _zget("contacts", params={"email": order.email})
            if res.get("contacts"): return res["contacts"][0]["contact_id"]
        except Exception:
            pass
    try:
        res = _zget("contacts", params={"contact_name": order.full_name})
        if res.get("contacts"): return res["contacts"][0]["contact_id"]
    except Exception:
        pass
    payload = {
        "contact_name": order.full_name or f"Guest {order.order_number}",
        "contact_type": "customer",
        "email": order.email or None,
        "phone": order.phone or None,
        "shipping_address": _build_address(order, include_phone=True),
        "billing_address":  _build_address(order, include_phone=True),
    }
    payload = _clean(payload)
    res = _zpost("contacts", payload)
    return (res.get("contact") or {}).get("contact_id")

# ------------ Payments ------------
def _create_payment_for_invoice(*, contact_id: str, invoice: dict, amount: float, mode: str) -> dict:
    inv = invoice.get("invoice") or {}
    inv_id = inv.get("invoice_id")
    if not inv_id:
        raise RuntimeError(f"Cannot determine invoice_id from response: {invoice}")
    payload = {
        "customer_id": contact_id,
        "payment_mode": mode,                  # "Cash" / "Online" / etc.
        "amount": float(amount),
        "date": time.strftime("%Y-%m-%d"),
        "invoices": [{"invoice_id": inv_id, "amount_applied": float(amount)}],
    }
    return _zpost("customerpayments", payload)

def _record_cod_payment(*, customer_id: str, invoice_id: str, amount: Decimal):
    payload = {
        "customer_id": customer_id,
        "payment_mode": PAYMENT_MODE_COD,
        "date": time.strftime("%Y-%m-%d"),
        "amount": float(amount),
        "invoices": [{"invoice_id": invoice_id, "amount_applied": float(amount)}],
    }
    return _zpost("customerpayments", payload)

# ------------ Sales Order / Invoice helpers ------------
def _create_sales_order(*, order: Order, contact_id: str) -> dict:
    # Prefer Zoho’s saved address IDs to avoid field-length issues
    contact = _zget(f"contacts/{contact_id}").get("contact", {}) or {}
    sa_id = (contact.get("shipping_address") or {}).get("address_id")
    ba_id = (contact.get("billing_address")  or {}).get("address_id")
    so_payload = {
        "customer_id": contact_id,
        "reference_number": order.order_number,
        "date": time.strftime("%Y-%m-%d"),
        "line_items": _line_items(order),
        **({"shipping_address_id": sa_id} if sa_id else {}),
        **({"billing_address_id":  ba_id} if ba_id else {}),
        "customer_notes": (order.shipping_address_text or "")[:200],
    }
    if DEBUG_ZOHO:
        print("🟢 POST Sales Order payload:\n", json.dumps(so_payload, indent=2, ensure_ascii=False))
    return _zpost("salesorders", so_payload)

def _confirm_sales_order(salesorder_id: str) -> None:
    _zpost(f"salesorders/{salesorder_id}/status/confirmed", {})

def _fetch_salesorder(so_id: str) -> dict:
    return _zget(f"salesorders/{so_id}").get("salesorder", {}) or {}

def _so_to_invoice_payload(so: dict, *, customer_id: str) -> dict:
    """
    Build an invoice payload using the SO's concrete line items (with item_id).
    This avoids Zoho's 'You haven't selected any items!' error.
    """
    items = []
    for li in (so.get("line_items") or []):
        items.append({
            "item_id": li.get("item_id"),
            "name": li.get("name"),
            "rate": float(li.get("rate") or 0),
            "quantity": float(li.get("quantity") or 0),
            "salesorder_item_id": li.get("line_item_id") or li.get("salesorder_item_id"),
        })

    payload = {
        "customer_id": customer_id,
        "reference_number": so.get("reference_number"),
        "date": time.strftime("%Y-%m-%d"),
        "salesorder_id": so.get("salesorder_id"),
        "line_items": items,
    }

    # Reuse Zoho's address IDs if present on the SO
    if so.get("shipping_address_id"):
        payload["shipping_address_id"] = so["shipping_address_id"]
    if so.get("billing_address_id"):
        payload["billing_address_id"] = so["billing_address_id"]

    return payload

def _convert_so_to_invoice(salesorder_id: str, *, customer_id: str):
    """
    Convert a Sales Order to an Invoice by explicitly sending its line_items.
    """
    so = _fetch_salesorder(salesorder_id)
    if not so or not (so.get("line_items") or []):
        raise RuntimeError(f"Sales Order {salesorder_id} has no line items.")
    payload = _so_to_invoice_payload(so, customer_id=customer_id)
    return _zpost("invoices", payload)

# ------------ Public entrypoint ------------
def push_order_to_zoho(order: Order):
    """
    Pipeline:
      1) Ensure/lookup Zoho Contact
      2) Create Sales Order (dashboard visibility)
      3) Confirm Sales Order
      4) Convert SO → Invoice (with items) → deducts stock
      5) (Optional) Record payment: COD → Cash, Online → Online
    """
    try:
        # 1) Ensure customer
        contact_id = _ensure_customer(order)

        # 2) Create Sales Order
        so_res = _create_sales_order(order=order, contact_id=contact_id)
        salesorder = (so_res.get("salesorder") or {})
        so_id = salesorder.get("salesorder_id")
        if not so_id:
            raise RuntimeError(f"No salesorder_id in response: {so_res}")

        # 3) Confirm SO
        _confirm_sales_order(so_id)

        # 4) Convert to Invoice (send SO items explicitly)
        inv_res = _convert_so_to_invoice(so_id, customer_id=contact_id)
        invoice = (inv_res.get("invoice") or {})
        invoice_id = invoice.get("invoice_id")
        if not invoice_id:
            raise RuntimeError(f"No invoice_id in response: {inv_res}")

        # 5) Mark as paid (optional)
        if AUTO_MARK_PAID:
            is_cod = (order.payment_method or "").lower() == "cod"
            pay_mode = PAYMENT_MODE_COD if is_cod else PAYMENT_MODE_ONLINE
            # Use the invoice total to match Zoho’s tax/rounding
            pay_amount = Decimal(str(invoice.get("total") or invoice.get("balance") or order.grand_total or "0"))
            _zpost("customerpayments", {
                "customer_id": contact_id,
                "payment_mode": pay_mode,
                "date": time.strftime("%Y-%m-%d"),
                "amount": float(pay_amount),
                "invoices": [{"invoice_id": invoice_id, "amount_applied": float(pay_amount)}],
            })

        print(f"✅ Order {order.order_number}: SO {so_id} → Invoice {invoice.get('invoice_number')} {'(paid)' if AUTO_MARK_PAID else ''}")
    except Exception:
        log.exception("Zoho push failed for %s", order.order_number)
