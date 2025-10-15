#!/usr/bin/env python
"""Test complete Zoho sync for most recent order."""

import os
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Order
from myApp.integrations.zoho_inventory import push_order_to_zoho

# Get most recent order
order = Order.objects.latest('created_at')

print(f"\n{'='*80}")
print(f"TESTING ZOHO SYNC FOR ORDER: {order.order_number}")
print(f"{'='*80}\n")

print(f"Order Details:")
print(f"  Customer: {order.full_name}")
print(f"  Items: {order.items.count()}")
print(f"  Created: {order.created_at}\n")

print(f"Starting Zoho sync...\n")

try:
    push_order_to_zoho(order)
    print(f"\n{'='*80}")
    print(f"✅ SYNC COMPLETED SUCCESSFULLY!")
    print(f"{'='*80}\n")
except Exception as e:
    print(f"\n{'='*80}")
    print(f"❌ SYNC FAILED: {e}")
    print(f"{'='*80}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)



