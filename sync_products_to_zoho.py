# -*- coding: utf-8 -*-
import os, sys, time, json
from decimal import Decimal
import requests

# ------------ Django bootstrap ------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Product

# ------------ Config ------------
DEBUG_ZOHO = False           # set True to print URLs & payloads
SLEEP = 0.3

ZOHO = dict(
    CLIENT_ID=os.getenv("ZOHO_CLIENT_ID", ""),
    CLIENT_SECRET=os.getenv("ZOHO_CLIENT_SECRET", ""),
    REFRESH_TOKEN=os.getenv("ZOHO_REFRESH_TOKEN", ""),
    ORG_ID=os.getenv("ZOHO_ORG_ID", ""),
    BASE=(os.getenv("ZOHO_BASE", "https://www.zohoapis.com") or "https://www.zohoapis.com").rstrip("/"),
)

def _accounts_from_base(api_base: str) -> str:
    if "zohoapis.eu" in api_base: return "https://accounts.zoho.eu"
    if "zohoapis.in" in api_base: return "https://accounts.zoho.in"
    return "https://accounts.zoho.com"

_TOK, _TOK_EXP = None, 0
def _access_token() -> str:
    global _TOK, _TOK_EXP
    now = time.time()
    if _TOK and now < _TOK_EXP - 60:
        return _TOK
    url = f"{_accounts_from_base(ZOHO['BASE'])}/oauth/v2/token"
    data = {
        "refresh_token": ZOHO["REFRESH_TOKEN"],
        "client_id": ZOHO["CLIENT_ID"],
        "client_secret": ZOHO["CLIENT_SECRET"],
        "grant_type": "refresh_token",
    }
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    js = r.json()
    _TOK = js["access_token"]
    _TOK_EXP = now + int(js.get("expires_in", 3600))
    return _TOK

def _api_url(path: str) -> str:
    return f"{ZOHO['BASE'].rstrip('/')}/inventory/v1/{path.lstrip('/')}"

def _headers_form():
    return {
        "Authorization": f"Zoho-oauthtoken {_access_token()}",
        "X-com-zoho-inventory-organizationid": str(ZOHO["ORG_ID"]),
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "application/json",
    }

# ------------ HTTP helpers ------------
def _zget(path, params=None):
    url = _api_url(path)
    p = {"organization_id": ZOHO["ORG_ID"]}
    if params: p.update(params)
    if DEBUG_ZOHO: print(f"[GET]  {url}  params={p}")
    r = requests.get(url, headers={
        "Authorization": f"Zoho-oauthtoken {_access_token()}",
        "X-com-zoho-inventory-organizationid": str(ZOHO["ORG_ID"]),
        "Accept": "application/json"}, params=p, timeout=30)
    r.raise_for_status()
    return r.json()

def _zpost(path, payload_dict):
    url = _api_url(path)
    data = {"JSONString": json.dumps(payload_dict)}
    if DEBUG_ZOHO:
        print(f"[POST] {url}\n{json.dumps(payload_dict, indent=2)[:1200]}")
    r = requests.post(url, headers=_headers_form(),
                      params={"organization_id": ZOHO["ORG_ID"]}, data=data, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"POST {url} -> {r.status_code}: {r.text}")
    return r.json()

def _zput(path, payload_dict):
    url = _api_url(path)
    data = {"JSONString": json.dumps(payload_dict)}
    if DEBUG_ZOHO:
        print(f"[PUT]  {url}\n{json.dumps(payload_dict, indent=2)[:1200]}")
    r = requests.put(url, headers=_headers_form(),
                     params={"organization_id": ZOHO["ORG_ID"]}, data=data, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"PUT {url} -> {r.status_code}: {r.text}")
    return r.json()

# ------------ Index helpers ------------
class _Index:
    def __init__(self):
        self.by_sku, self.by_name = {}, {}

def _list_all(path, key):
    idx = _Index()
    page = 1
    while True:
        res = _zget(path, params={"page": page, "per_page": 200})
        items = res.get(key) or []
        for it in items:
            sku = (it.get("sku") or "").strip()
            name = (it.get("name") or "").strip()
            if sku: idx.by_sku[sku] = it
            if name: idx.by_name[name] = it
        if len(items) < 200: break
        page += 1
        time.sleep(SLEEP)
    return idx

# ------------ Payload builders ------------
def _item_payload_from_product(p: Product):
    name = (p.name or "").strip()[:100]
    if not name:
        raise ValueError("Product name is empty after trimming.")

    # NOTE: intentionally NO `is_taxable` here (Zoho rejected it)
    return {
        "name": name,
        "sku": (p.sku or "").strip()[:200] or None,
        "product_type": "goods",
        "unit": "pcs",
        "is_sales": True,
        "is_purchase": True,
        "rate": float(p.price),          # selling price
        "purchase_rate": 0.0,            # cost price if you track it
        "description": (p.short_description or p.description or "").strip()[:32000] or None,
    }

def _composite_payload_from_bundle(b: Product, comp_ids):
    name = (b.name or "").strip()[:100]
    return {
        "name": name,
        "sku": (b.sku or "").strip()[:200] or None,
        "product_type": "goods",
        "unit": "pcs",
        "rate": float(b.price),
        "description": (b.short_description or b.description or "").strip()[:32000] or None,
        "is_combo_product": True,              # 👈 required for bundles
        "mapped_items": [                      # 👈 this key name is what Zoho expects
            {"item_id": iid, "quantity": int(qty)}
            for iid, qty in comp_ids
        ],
    }


# ------------ Sync ------------
def _ensure_item(p: Product, items_idx: _Index) -> dict:
    z = None
    if p.sku and p.sku in items_idx.by_sku:
        z = items_idx.by_sku[p.sku]
    elif p.name in items_idx.by_name:
        z = items_idx.by_name[p.name]

    payload = _item_payload_from_product(p)

    if z:
        res = _zput(f"items/{z['item_id']}", payload)
        out = res.get("item") or z
        print(f"↑ Updated item: {p.name} (SKU: {p.sku or '—'})")
    else:
        res = _zpost("items", payload)
        out = res.get("item")
        print(f"+ Created item: {p.name} (SKU: {p.sku or '—'})")

    if p.sku: items_idx.by_sku[p.sku] = out
    items_idx.by_name[p.name] = out
    time.sleep(SLEEP)
    return out

def _ensure_composite(bundle: Product, comps, items_idx: _Index, comp_idx: _Index) -> dict:
    # make sure all components exist as normal items
    comp_ids = []
    for comp, qty in comps:
        z = None
        if comp.sku and comp.sku in items_idx.by_sku:
            z = items_idx.by_sku[comp.sku]
        elif comp.name in items_idx.by_name:
            z = items_idx.by_name[comp.name]
        else:
            z = _ensure_item(comp, items_idx)
        comp_ids.append((z["item_id"], qty))

    zc = None
    if bundle.sku and bundle.sku in comp_idx.by_sku:
        zc = comp_idx.by_sku[bundle.sku]
    elif bundle.name in comp_idx.by_name:
        zc = comp_idx.by_name[bundle.name]

    payload = _composite_payload_from_bundle(bundle, comp_ids)

    if zc:
        res = _zput(f"compositeitems/{zc['composite_item_id']}", payload)
        out = res.get("composite_item") or zc
        print(f"↑ Updated composite: {bundle.name}")
    else:
        res = _zpost("compositeitems", payload)
        out = res.get("composite_item")
        print(f"+ Created composite: {bundle.name}")

    if bundle.sku: comp_idx.by_sku[bundle.sku] = out
    comp_idx.by_name[bundle.name] = out
    time.sleep(SLEEP)
    return out

def main():
    missing = [k for k, v in ZOHO.items() if not v and k not in ("BASE",)]
    if missing:
        print("❌ Missing Zoho env vars:", ", ".join(missing)); sys.exit(2)

    print("🔄 Fetching existing Zoho Items & Composites …")
    items_idx = _list_all("items", "items")
    comp_idx  = _list_all("compositeitems", "composite_items")

    # 1) Singles
    for p in Product.objects.filter(is_active=True, is_bundle=False).order_by("name"):
        try:
            _ensure_item(p, items_idx)
        except Exception as e:
            print(f"‼️ Item sync failed for {p.name}: {e}")

    # 2) Bundles
    qs = Product.objects.filter(is_active=True, is_bundle=True).prefetch_related("component_links__component")
    for b in qs:
        comps = [(link.component, int(link.quantity or 1)) for link in b.component_links.all()]
        if not comps:
            print(f"⚠️ Skipping empty bundle {b.name}")
            continue
        try:
            _ensure_composite(b, comps, items_idx, comp_idx)
        except Exception as e:
            print(f"‼️ Composite sync failed for {b.name}: {e}")

    print("✅ Sync complete.")

if __name__ == "__main__":
    main()
