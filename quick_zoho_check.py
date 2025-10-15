#!/usr/bin/env python
"""Quick check: Last 5 orders vs Zoho status."""
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Order
from myApp.integrations.zoho_inventory import _get_access_token, _zget

print("QUICK ZOHO CHECK - Last 5 Orders")
print("=" * 60)

_get_access_token()
orders = Order.objects.all().order_by('-created_at')[:5]

for order in orders:
    print(f"\n{order.order_number} ({order.created_at.strftime('%Y-%m-%d %H:%M')})")
    
    # Check Zoho
    try:
        so = _zget("salesorders", params={"reference_number": order.order_number})
        inv = _zget("invoices", params={"reference_number": order.order_number})
        
        has_so = bool(so.get("salesorders"))
        has_inv = bool(inv.get("invoices"))
        
        if has_so and has_inv:
            print("  ✅ IN ZOHO (SO + Invoice)")
        elif has_so:
            print("  ⚠️  IN ZOHO (SO only, no Invoice)")
        else:
            print("  ❌ NOT IN ZOHO")
            
        # Check for stored error
        addr = order.shipping_address or {}
        if '_zoho_sync_error' in addr:
            err = addr['_zoho_sync_error']
            print(f"  🔴 Sync Error: {err.get('error', 'Unknown')[:80]}")
            
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 60)

