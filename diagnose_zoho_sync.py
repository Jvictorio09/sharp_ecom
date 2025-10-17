#!/usr/bin/env python
"""Diagnose why Zoho sync is not working."""

import os
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Order
from myApp.integrations.zoho_inventory import push_order_to_zoho, _zget

print("=" * 80)
print("ZOHO SYNC DIAGNOSTIC")
print("=" * 80)

# Get most recent order
recent_order = Order.objects.all().order_by('-created_at').first()

if not recent_order:
    print("\n❌ No orders found in database.")
    sys.exit(1)

print(f"\nMost Recent Order:")
print(f"  Order Number: {recent_order.order_number}")
print(f"  Customer: {recent_order.full_name}")
print(f"  Created: {recent_order.created_at}")
print(f"  Items: {recent_order.items.count()}")

# Check if in Zoho
print(f"\nChecking Zoho for order {recent_order.order_number}...")

try:
    # Check Sales Order
    so_result = _zget("salesorders", params={"reference_number": recent_order.order_number})
    salesorders = so_result.get("salesorders", [])
    
    if salesorders:
        print(f"  ✅ Sales Order EXISTS: {salesorders[0].get('salesorder_id')}")
        print(f"     Status: {salesorders[0].get('salesorder_status')}")
    else:
        print(f"  ❌ Sales Order NOT FOUND")
    
    # Check Invoice
    inv_result = _zget("invoices", params={"reference_number": recent_order.order_number})
    invoices = inv_result.get("invoices", [])
    
    if invoices:
        print(f"  ✅ Invoice EXISTS: {invoices[0].get('invoice_number')}")
        print(f"     Status: {invoices[0].get('status')}")
        print(f"     Total: {invoices[0].get('total')}")
    else:
        print(f"  ❌ Invoice NOT FOUND")

except Exception as e:
    print(f"  ❌ Error checking Zoho: {e}")
    import traceback
    traceback.print_exc()

# Try to sync now
print(f"\n{'='*80}")
response = input(f"Try to sync order {recent_order.order_number} to Zoho now? (y/N): ").strip().lower()

if response == 'y':
    print(f"\n🔄 Syncing to Zoho...")
    try:
        push_order_to_zoho(recent_order)
        print(f"✅ Sync completed!")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)




