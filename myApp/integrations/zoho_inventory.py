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
    r = requests.post(url, data=data, timeout=60)  # Increased to 60 seconds
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

def _retry_request(func, max_retries=3):
    """Retry wrapper for API calls with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.Timeout as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            log.warning(f"Zoho API timeout (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
            time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            # For other request errors, don't retry
            raise

def _zget(path, params=None):
    url = _api_url(path)
    p = {"organization_id": ZOHO_ORG_ID}
    if params: p.update(params)
    
    def make_request():
        r = requests.get(url, headers=_headers(), params=p, timeout=60)
        r.raise_for_status()
        return r.json()
    
    return _retry_request(make_request)

def _zpost(path, payload, params_extra=None):
    url = _api_url(path)
    if DEBUG_ZOHO:
        print(f"🟢 POST {url}")
        try:
            print(json.dumps(payload, indent=2, ensure_ascii=False)[:1200])
        except Exception:
            print(str(payload)[:1200])
    
    def make_request():
        params = {"organization_id": ZOHO_ORG_ID}
        if params_extra:
            params.update(params_extra)
        
        r = requests.post(url, headers=_headers(), params=params, json=payload, timeout=60)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            # Parse Zoho error code from response body
            error_code = None
            try:
                error_body = r.json()
                error_code = error_body.get('code')
            except Exception:
                pass
            
            # Include error code in exception for easier handling
            error_msg = f"POST {url} -> {r.status_code}"
            if error_code:
                error_msg += f" [Zoho code: {error_code}]"
            error_msg += f": {r.text[:2000]}"
            
            exc = RuntimeError(error_msg)
            exc.zoho_error_code = error_code  # Attach for easy checking
            raise exc from e
        return r.json()
    
    return _retry_request(make_request)

def _zput(path, payload):
    url = _api_url(path)
    
    def make_request():
        r = requests.put(url, headers=_headers(), params={"organization_id": ZOHO_ORG_ID}, json=payload, timeout=60)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            raise RuntimeError(f"PUT {url} -> {r.status_code}: {r.text[:2000]}") from e
        return r.json()
    
    return _retry_request(make_request)

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
def _find_existing_so_by_reference(order_number: str):
    """
    Search Zoho for existing Sales Order by salesorder_number or reference_number.
    Returns salesorder_id if found, None otherwise.
    """
    try:
        # Try salesorder_number search (our custom number)
        res = _zget("salesorders", params={"salesorder_number": order_number})
        candidates = res.get("salesorders", [])
        
        # Filter to exact match
        matches = [
            so for so in candidates 
            if so.get("salesorder_number") == order_number or so.get("reference_number") == order_number
        ]
        
        if not matches:
            # Fallback: reference_number search
            res = _zget("salesorders", params={"reference_number": order_number})
            candidates = res.get("salesorders", [])
            matches = [
                so for so in candidates 
                if so.get("salesorder_number") == order_number or so.get("reference_number") == order_number
            ]
        
        if not matches:
            # Last resort: searchtext
            res = _zget("salesorders", params={"searchtext": order_number})
            candidates = res.get("salesorders", [])
            matches = [
                so for so in candidates 
                if so.get("salesorder_number") == order_number or so.get("reference_number") == order_number
            ]
        
        if matches:
            so_id = matches[0].get("salesorder_id")
            so_num = matches[0].get("salesorder_number", order_number)
            log.info(f"Found existing SO {so_num} (ID: {so_id})")
            return so_id
        
        return None
    except Exception as e:
        log.warning(f"Error searching for SO {order_number}: {e}")
        return None


def _find_existing_invoice_by_reference(reference_number: str, salesorder_id: str = None):
    """
    Search Zoho for existing Invoice by reference_number or salesorder_id.
    Returns invoice_id if found, None otherwise.
    """
    try:
        # Try by reference_number
        res = _zget("invoices", params={"reference_number": reference_number})
        candidates = res.get("invoices", [])
        matches = [inv for inv in candidates if inv.get("reference_number") == reference_number]
        
        if not matches and salesorder_id:
            # Fallback: search by SO ID
            res = _zget("invoices", params={"salesorder_id": salesorder_id})
            candidates = res.get("invoices", [])
            matches = [
                inv for inv in candidates 
                if inv.get("salesorder_id") == salesorder_id and inv.get("reference_number") == reference_number
            ]
        
        if matches:
            inv_id = matches[0].get("invoice_id")
            inv_num = matches[0].get("invoice_number")
            log.info(f"Found existing Invoice for {reference_number}: {inv_num} ({inv_id})")
            return inv_id, matches[0]
        
        return None, None
    except Exception as e:
        log.warning(f"Error searching for Invoice {reference_number}: {e}")
        return None, None


def _create_sales_order(*, order: Order, contact_id: str) -> dict:
    # Prefer Zoho's saved address IDs to avoid field-length issues
    contact = _zget(f"contacts/{contact_id}").get("contact", {}) or {}
    sa_id = (contact.get("shipping_address") or {}).get("address_id")
    ba_id = (contact.get("billing_address")  or {}).get("address_id")
    so_payload = {
        "customer_id": contact_id,
        "salesorder_number": order.order_number,  # Our custom number (e.g., SH-694204)
        "reference_number": order.order_number,   # Also store in reference for searchability
        "date": time.strftime("%Y-%m-%d"),
        "line_items": _line_items(order),
        **({"shipping_address_id": sa_id} if sa_id else {}),
        **({"billing_address_id":  ba_id} if ba_id else {}),
        "customer_notes": (order.shipping_address_text or "")[:200],
    }
    if DEBUG_ZOHO:
        print("🟢 POST Sales Order payload:\n", json.dumps(so_payload, indent=2, ensure_ascii=False))
    
    # Add query param to use our custom number instead of Zoho's auto-generated one
    url = _api_url("salesorders")
    params = {
        "organization_id": ZOHO_ORG_ID,
        "ignore_auto_number_generation": "true"  # ✅ Accept our custom salesorder_number
    }
    
    def make_request():
        r = requests.post(url, headers=_headers(), params=params, json=so_payload, timeout=60)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            # Parse Zoho error code
            error_code = None
            try:
                error_body = r.json()
                error_code = error_body.get('code')
            except Exception:
                pass
            
            error_msg = f"POST {url} -> {r.status_code}"
            if error_code:
                error_msg += f" [Zoho code: {error_code}]"
            error_msg += f": {r.text[:2000]}"
            
            exc = RuntimeError(error_msg)
            exc.zoho_error_code = error_code
            raise exc from e
        return r.json()
    
    return _retry_request(make_request)

def _confirm_sales_order(salesorder_id: str) -> None:
    """Confirm a Sales Order (idempotent - if already confirmed, no error)."""
    _zpost(f"salesorders/{salesorder_id}/status/confirmed", {})

def _convert_so_to_invoice(salesorder_id: str):
    """
    Convert a Sales Order to an Invoice using Zoho's built-in conversion.
    
    Pre-check: Ensures SO is confirmed before conversion.
    Conversion: Uses query param ?salesorder_id=xxx to inherit all SO fields automatically
                (line items, addresses, locations, custom fields, etc.)
    
    Reference: https://www.zoho.com/books/api/v3/invoices/#create-an-invoice-from-a-sales-order
    """
    # Pre-check: Get SO status
    try:
        so_res = _zget(f"salesorders/{salesorder_id}")
        so = so_res.get("salesorder", {})
        status = so.get("status", "").lower()
        
        # If not confirmed, confirm it first
        if status != "confirmed":
            if DEBUG_ZOHO:
                print(f"🔄 SO status is '{status}', confirming before conversion...")
            _confirm_sales_order(salesorder_id)
    except Exception as e:
        # If we can't check status, try to confirm anyway (idempotent)
        log.warning(f"Could not check SO status for {salesorder_id}, attempting confirm: {e}")
        try:
            _confirm_sales_order(salesorder_id)
        except Exception:
            pass  # If confirm fails, conversion will fail with clearer error
    
    # Convert SO → Invoice using query param
    return _zpost("invoices/fromsalesorder", {}, params_extra={"salesorder_id": salesorder_id})

# ------------ Public entrypoint (clean & idempotent) ------------
def push_order_to_zoho(order: Order):
    """
    Idempotent Zoho sync pipeline:
      1) Ensure/lookup Zoho Contact
      2) Get/Create Sales Order (stored ID first, create with custom salesorder_number, handle 36004 gracefully)
      3) Get/Create Invoice from SO (auto-confirms SO if needed, uses query param conversion)
      4) Record payment (if AUTO_MARK_PAID)
      
    Key: We send salesorder_number = order.order_number (e.g., SH-694204) with 
         ignore_auto_number_generation=true so our custom number appears in Zoho.
         Invoice conversion handles SO confirmation automatically.
         All duplicates are handled gracefully - no crashes, always completes.
    """
    try:
        zoho_data = dict(order.zoho_data or {})
        
        # 1) Ensure customer contact
        contact_id = zoho_data.get('contact_id')
        if not contact_id:
            contact_id = _ensure_customer(order)
            zoho_data['contact_id'] = contact_id
            order.zoho_data = zoho_data
            order.save(update_fields=['zoho_data'])

        # 2) Get or Create Sales Order (idempotent)
        so_id = zoho_data.get('salesorder_id')
        
        if so_id:
            # Already synced - use stored ID
            print(f"📌 Using stored SO: {so_id}")
            log.info(f"Reusing salesorder_id for {order.order_number}: {so_id}")
        else:
            # Try to create new SO
            try:
                so_res = _create_sales_order(order=order, contact_id=contact_id)
                so_id = (so_res.get("salesorder") or {}).get("salesorder_id")
                
                if not so_id:
                    raise RuntimeError(f"No salesorder_id in response: {so_res}")
                
                # Success - store it
                zoho_data['salesorder_id'] = so_id
                zoho_data['synced_at'] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                order.zoho_data = zoho_data
                order.save(update_fields=['zoho_data'])
                
                print(f"✅ Created SO {so_id} for {order.order_number}")
                log.info(f"Created salesorder_id {so_id} for {order.order_number}")
                
            except RuntimeError as e:
                # Check for duplicate error (36004)
                error_code = getattr(e, 'zoho_error_code', None)
                is_duplicate = (error_code == 36004) or ("36004" in str(e)) or ("already exists" in str(e).lower())
                
                if is_duplicate:
                    # Duplicate detected - find and reuse existing SO
                    print(f"♻️  SO already exists for {order.order_number}, searching...")
                    log.info(f"Duplicate SO detected for {order.order_number}, searching Zoho")
                    
                    so_id = _find_existing_so_by_reference(order.order_number)
                    
                    if so_id:
                        # Found it - store and continue
                        zoho_data['salesorder_id'] = so_id
                        order.zoho_data = zoho_data
                        order.save(update_fields=['zoho_data'])
                        print(f"✅ Found & stored existing SO: {so_id}")
                    else:
                        # Couldn't find it even though Zoho said it exists - abort
                        raise RuntimeError(f"SO exists for {order.order_number} but couldn't retrieve it") from e
                else:
                    # Different error - re-raise
                    raise

        # 3) Get or Create Invoice (idempotent)
        # Note: _convert_so_to_invoice handles SO confirmation automatically
        invoice_id = zoho_data.get('invoice_id')
        invoice = {}
        
        if invoice_id:
            # Already have invoice - fetch its details
            print(f"📌 Using stored Invoice: {invoice_id}")
            log.info(f"Reusing invoice_id for {order.order_number}: {invoice_id}")
            
            try:
                inv_res = _zget(f"invoices/{invoice_id}")
                invoice = (inv_res.get("invoice") or {})
            except Exception as e:
                log.warning(f"Stored invoice_id {invoice_id} not accessible: {e}")
                # Clear it and try to create/find
                invoice_id = None
        
        if not invoice_id:
            # Try to create invoice from SO (Zoho auto-copies all fields)
            try:
                inv_res = _convert_so_to_invoice(so_id)
                invoice = (inv_res.get("invoice") or {})
                invoice_id = invoice.get("invoice_id")
                
                if not invoice_id:
                    raise RuntimeError(f"No invoice_id in response: {inv_res}")
                
                # Success - store it
                zoho_data['invoice_id'] = invoice_id
                order.zoho_data = zoho_data
                order.save(update_fields=['zoho_data'])
                
                inv_num = invoice.get('invoice_number', 'N/A')
                print(f"✅ Created Invoice {inv_num} ({invoice_id}) for {order.order_number}")
                log.info(f"Created invoice {inv_num} for {order.order_number}")
                
            except RuntimeError as e:
                # Check for duplicate or "contact change" errors
                error_code = getattr(e, 'zoho_error_code', None)
                is_duplicate = (
                    (error_code == 36024) or 
                    ("36024" in str(e)) or 
                    ("not allowed to change" in str(e).lower()) or
                    ("already exists" in str(e).lower())
                )
                
                if is_duplicate:
                    # Duplicate invoice - find and reuse
                    print(f"♻️  Invoice already exists for {order.order_number}, searching...")
                    log.info(f"Duplicate invoice detected for {order.order_number}, searching Zoho")
                    
                    invoice_id, invoice = _find_existing_invoice_by_reference(order.order_number, so_id)
                    
                    if invoice_id:
                        # Found it - store and continue
                        zoho_data['invoice_id'] = invoice_id
                        order.zoho_data = zoho_data
                        order.save(update_fields=['zoho_data'])
                        
                        inv_num = invoice.get('invoice_number', 'N/A')
                        print(f"✅ Found & stored existing Invoice: {inv_num} ({invoice_id})")
                    else:
                        # Couldn't find it - abort
                        raise RuntimeError(f"Invoice exists for {order.order_number} but couldn't retrieve it") from e
                else:
                    # Different error - re-raise
                    raise

        # 5) Record payment (optional, best-effort)
        if AUTO_MARK_PAID:
            invoice_status = invoice.get("status", "").lower()
            
            if invoice_status not in ["paid", "void"]:
                is_cod = (order.payment_method or "").lower() == "cod"
                pay_mode = PAYMENT_MODE_COD if is_cod else PAYMENT_MODE_ONLINE
                pay_amount = Decimal(str(invoice.get("total") or invoice.get("balance") or order.grand_total or "0"))
                
                try:
                    _zpost("customerpayments", {
                        "customer_id": contact_id,
                        "payment_mode": pay_mode,
                        "date": time.strftime("%Y-%m-%d"),
                        "amount": float(pay_amount),
                        "invoices": [{"invoice_id": invoice_id, "amount_applied": float(pay_amount)}],
                    })
                    log.info(f"Recorded payment for {order.order_number}: {pay_mode} {pay_amount}")
                except Exception as pay_err:
                    # Payment recording failed - log but don't crash
                    log.warning(f"Could not record payment for {order.order_number}: {pay_err}")
            else:
                log.info(f"Invoice {invoice_id} already {invoice_status}, skipping payment")

        # Success summary
        inv_num = invoice.get('invoice_number', 'N/A')
        print(f"✅ Sync complete: {order.order_number} → SO {so_id} → Invoice {inv_num}")
        
    except Exception as e:
        # Final catch-all - log but don't crash the checkout
        log.exception(f"Zoho sync failed for {order.order_number}: {e}")
        print(f"❌ Zoho sync failed for {order.order_number}: {e}")
        # Don't re-raise - order is created locally, Zoho sync can be retried later
