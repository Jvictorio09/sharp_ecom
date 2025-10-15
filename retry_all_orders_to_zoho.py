#!/usr/bin/env python
"""
Retry Zoho sync for all orders that might have failed.
This script:
1. Finds all orders
2. Checks if they exist in Zoho
3. Syncs any that are missing
"""

import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Order
from myApp.integrations.zoho_inventory import push_order_to_zoho, _get_access_token, _zget

def check_order_in_zoho(order_number):
    """Check if order exists in Zoho (both SO and Invoice)."""
    try:
        # Check Sales Order
        so_result = _zget("salesorders", params={"reference_number": order_number})
        has_so = bool(so_result.get("salesorders", []))
        
        # Check Invoice
        inv_result = _zget("invoices", params={"reference_number": order_number})
        has_invoice = bool(inv_result.get("invoices", []))
        
        return has_so, has_invoice
    except Exception as e:
        print(f"  Error checking {order_number}: {e}")
        return False, False

def main():
    print("=" * 80)
    print("RETRY ZOHO SYNC - ALL ORDERS")
    print("=" * 80)
    
    # Connect
    print("\nConnecting to Zoho...")
    _get_access_token()
    print("Connected!\n")
    
    # Get all orders (or filter by date)
    print("Fetching orders from database...")
    orders = Order.objects.all().order_by('-created_at')
    print(f"Found {len(orders)} orders\n")
    
    print("=" * 80)
    
    missing_orders = []
    synced_orders = []
    failed_orders = []
    
    # Check each order
    for idx, order in enumerate(orders, 1):
        print(f"\n[{idx}/{len(orders)}] Checking: {order.order_number}")
        print(f"  Created: {order.created_at}")
        print(f"  Total: ${order.grand_total}")
        
        has_so, has_invoice = check_order_in_zoho(order.order_number)
        
        if has_so and has_invoice:
            print(f"  ✅ Already in Zoho (SO + Invoice)")
            synced_orders.append(order.order_number)
        elif has_so and not has_invoice:
            print(f"  ⚠️  Has SO but no Invoice - will retry")
            missing_orders.append(order)
        else:
            print(f"  ❌ Missing from Zoho - will sync")
            missing_orders.append(order)
        
        # Rate limit
        time.sleep(0.3)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Already synced: {len(synced_orders)}")
    print(f"❌ Need to sync: {len(missing_orders)}")
    print("=" * 80)
    
    if not missing_orders:
        print("\n🎉 All orders are already in Zoho!")
        return
    
    print(f"\n⚠️  Found {len(missing_orders)} orders missing from Zoho")
    print("\nOrders to sync:")
    for order in missing_orders[:10]:
        print(f"  - {order.order_number} ({order.created_at.strftime('%Y-%m-%d')})")
    if len(missing_orders) > 10:
        print(f"  ... and {len(missing_orders) - 10} more")
    
    response = input(f"\nSync {len(missing_orders)} orders to Zoho? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Cancelled by user")
        return
    
    print("\n" + "=" * 80)
    print("SYNCING TO ZOHO")
    print("=" * 80)
    
    # Sync each missing order
    for idx, order in enumerate(missing_orders, 1):
        print(f"\n[{idx}/{len(missing_orders)}] Syncing: {order.order_number}")
        
        try:
            push_order_to_zoho(order)
            print(f"  ✅ SUCCESS")
            synced_orders.append(order.order_number)
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed_orders.append((order.order_number, str(e)))
            # Continue with next order
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"✅ Successfully synced: {len(synced_orders)}")
    print(f"❌ Failed: {len(failed_orders)}")
    
    if failed_orders:
        print("\nFailed orders:")
        for order_num, error in failed_orders:
            print(f"  - {order_num}: {error[:100]}")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

