#!/usr/bin/env python
"""Check recent orders and their Zoho sync status."""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Order
from myApp.integrations.zoho_inventory import _get_access_token, _zget

# Get last 10 orders
orders = Order.objects.all().order_by('-created_at')[:10]

print("=" * 80)
print("RECENT ORDERS - ZOHO SYNC CHECK")
print("=" * 80)

_get_access_token()

for order in orders:
    print(f"\nOrder: {order.order_number}")
    print(f"  Created: {order.created_at}")
    print(f"  Status: {order.status}")
    print(f"  Payment: {order.payment_method}")
    
    # Check if in Zoho
    try:
        result = _zget("salesorders", params={"reference_number": order.order_number})
        so = result.get("salesorders", [])
        if so:
            print(f"  Zoho SO: EXISTS - {so[0].get('salesorder_number')}")
        else:
            print(f"  Zoho SO: NOT FOUND")
        
        inv_result = _zget("invoices", params={"reference_number": order.order_number})
        inv = inv_result.get("invoices", [])
        if inv:
            print(f"  Zoho Invoice: EXISTS - {inv[0].get('invoice_number')}")
        else:
            print(f"  Zoho Invoice: NOT FOUND")
    except Exception as e:
        print(f"  ERROR checking Zoho: {e}")

print("\n" + "=" * 80)

