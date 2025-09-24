# test_zoho.py  (place next to manage.py)

import os, sys, json, requests

# --- Bootstrap Django settings (same pattern as your other scripts)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")  # <-- change if your settings module differs
import django
django.setup()

from django.conf import settings
from django.core.cache import cache

# Pull config from settings.ZOHO (preferred) or .env
ZOHO = getattr(settings, "ZOHO", {}) or {
    "CLIENT_ID":     os.getenv("ZOHO_CLIENT_ID"),
    "CLIENT_SECRET": os.getenv("ZOHO_CLIENT_SECRET"),
    "REFRESH_TOKEN": os.getenv("ZOHO_REFRESH_TOKEN"),
    "ORG_ID":        os.getenv("ZOHO_ORG_ID"),
    "BASE":          os.getenv("ZOHO_BASE", "https://www.zohoapis.com"),
}

def _accounts_from_base(api_base: str) -> str:
    # Map api domain -> accounts domain (US/EU/IN)
    if "zohoapis.eu" in api_base:   return "https://accounts.zoho.eu"
    if "zohoapis.in" in api_base:   return "https://accounts.zoho.in"
    return "https://accounts.zoho.com"  # default (US)

def _get_access_token() -> str:
    """Exchange refresh token for access token (cached)."""
    key = "zoho_access_token:test"
    tok = cache.get(key)
    if tok:
        return tok

    accounts = _accounts_from_base(ZOHO["BASE"])
    url = f"{accounts}/oauth/v2/token"
    data = {
        "refresh_token": ZOHO["REFRESH_TOKEN"],
        "client_id": ZOHO["CLIENT_ID"],
        "client_secret": ZOHO["CLIENT_SECRET"],
        "grant_type": "refresh_token",
    }
    r = requests.post(url, data=data, timeout=20)
    try:
        r.raise_for_status()
    except Exception:
        print("❌ Token refresh failed")
        print("Status:", r.status_code)
        print("Body  :", (r.text or "")[:800])
        sys.exit(1)

    token = r.json().get("access_token")
    if not token:
        print("❌ No access_token in response:", r.text)
        sys.exit(1)

    cache.set(key, token, 3000)  # ~50 min
    return token

def main():
    required = ("CLIENT_ID","CLIENT_SECRET","REFRESH_TOKEN","ORG_ID","BASE")
    missing = [k for k in required if not ZOHO.get(k)]
    if missing:
        print("❌ Missing ZOHO config:", ", ".join(missing))
        sys.exit(1)

    token = _get_access_token()

    url = f"{ZOHO['BASE'].rstrip('/')}/inventory/v1/items?per_page=5"
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "X-com-zoho-inventory-organizationid": str(ZOHO["ORG_ID"]),
        "Accept": "application/json",
    }
    r = requests.get(url, headers=headers, timeout=20)
    try:
        r.raise_for_status()
    except Exception:
        print("❌ API call failed")
        print("URL   :", url)
        print("Status:", r.status_code)
        print("Body  :", (r.text or "")[:800])
        sys.exit(1)

    data = r.json()
    print("✅ Zoho API call successful")
    items = data.get("items", [])
    if not items:
        print("(No items returned — that’s okay if your Zoho inventory is empty.)")
    else:
        for it in items:
            print(f"- {it.get('name')}  (SKU: {it.get('sku') or '—'})")

if __name__ == "__main__":
    main()
