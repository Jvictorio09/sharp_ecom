#!/usr/bin/env python
"""
Retry Failed Zoho Sync
Manually sync orders that failed to sync to Zoho due to timeouts or errors.
"""

import os
import sys
from datetime import datetime, timedelta

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Order
from myApp.integrations.zoho_inventory import push_order_to_zoho, _zget

def check_order_in_zoho(order_number):
    """Check if an order has been synced to Zoho by looking for invoices."""
    try:
        result = _zget("invoices", params={"reference_number": order_number})
        invoices = result.get("invoices", [])
        return len(invoices) > 0, invoices
    except Exception as e:
        print(f"   ⚠️  Error checking Zoho: {e}")
        return None, []

def retry_single_order(order_number):
    """Retry sync for a single order."""
    print(f"\n{'='*80}")
    print(f"RETRYING ORDER: {order_number}")
    print(f"{'='*80}")
    
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        print(f"❌ Order {order_number} not found in database.")
        return False
    
    print(f"Order Details:")
    print(f"  - Customer: {order.full_name}")
    print(f"  - Email: {order.email}")
    print(f"  - Created: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  - Status: {order.get_status_display()}")
    print(f"  - Items: {order.items.count()}")
    
    # Check if already in Zoho
    print(f"\nChecking if already synced to Zoho...")
    in_zoho, invoices = check_order_in_zoho(order_number)
    
    if in_zoho:
        print(f"✅ Order already synced to Zoho!")
        print(f"   Invoice(s): {', '.join(inv.get('invoice_number') for inv in invoices)}")
        
        response = input(f"\nSync again anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping...")
            return True
    elif in_zoho is None:
        print(f"⚠️  Could not verify Zoho status, proceeding with sync...")
    else:
        print(f"❌ Not found in Zoho, will sync now...")
    
    # Attempt sync
    print(f"\n🔄 Syncing to Zoho...")
    try:
        push_order_to_zoho(order)
        print(f"✅ Successfully synced order {order_number} to Zoho!")
        
        # Verify
        print(f"\nVerifying sync...")
        in_zoho, invoices = check_order_in_zoho(order_number)
        if in_zoho:
            print(f"✅ Confirmed! Invoice created: {invoices[0].get('invoice_number')}")
            return True
        else:
            print(f"⚠️  Sync completed but invoice not found yet (may need refresh)")
            return True
            
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_and_retry_failed_orders(days_back=7):
    """Find orders that may not be synced and retry them."""
    print(f"\n{'='*80}")
    print(f"FINDING POTENTIALLY FAILED ORDERS (Last {days_back} days)")
    print(f"{'='*80}\n")
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    recent_orders = Order.objects.filter(created_at__gte=cutoff_date).order_by('-created_at')
    
    if not recent_orders:
        print(f"No orders found in the last {days_back} days.")
        return
    
    print(f"Found {recent_orders.count()} orders to check...\n")
    
    failed_orders = []
    synced_orders = []
    check_errors = []
    
    for order in recent_orders:
        print(f"Checking {order.order_number}...", end=" ")
        
        in_zoho, invoices = check_order_in_zoho(order.order_number)
        
        if in_zoho:
            print(f"✅ Synced")
            synced_orders.append(order)
        elif in_zoho is None:
            print(f"⚠️  Error checking")
            check_errors.append(order)
        else:
            print(f"❌ NOT in Zoho")
            failed_orders.append(order)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Already synced: {len(synced_orders)}")
    print(f"❌ Failed/Not synced: {len(failed_orders)}")
    print(f"⚠️  Check errors: {len(check_errors)}")
    
    if not failed_orders:
        print(f"\n🎉 All orders are synced to Zoho!")
        return
    
    # Show failed orders
    print(f"\n❌ Orders NOT in Zoho:")
    for order in failed_orders:
        print(f"   - {order.order_number} ({order.created_at.strftime('%Y-%m-%d %H:%M')})")
    
    # Offer to retry
    print(f"\n{'='*80}")
    response = input(f"Retry {len(failed_orders)} failed order(s)? (y/N): ").strip().lower()
    
    if response == 'y':
        print(f"\nRetrying failed orders...\n")
        success_count = 0
        for order in failed_orders:
            if retry_single_order(order.order_number):
                success_count += 1
        
        print(f"\n{'='*80}")
        print(f"RETRY RESULTS")
        print(f"{'='*80}")
        print(f"✅ Successfully synced: {success_count}/{len(failed_orders)}")
        print(f"❌ Failed: {len(failed_orders) - success_count}/{len(failed_orders)}")

def main():
    """Main menu."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "RETRY FAILED ZOHO SYNC" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    while True:
        print("\nOptions:")
        print("1. Retry specific order (by order number)")
        print("2. Find and retry failed orders (auto-detect)")
        print("3. List recent orders with sync status")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-3): ").strip()
        
        if choice == "1":
            order_num = input("Enter order number: ").strip()
            if order_num:
                retry_single_order(order_num)
        
        elif choice == "2":
            days = input("Check orders from last X days (default 7): ").strip()
            days_back = int(days) if days.isdigit() else 7
            find_and_retry_failed_orders(days_back)
        
        elif choice == "3":
            days = input("Show orders from last X days (default 7): ").strip()
            days_back = int(days) if days.isdigit() else 7
            
            cutoff = datetime.now() - timedelta(days=days_back)
            orders = Order.objects.filter(created_at__gte=cutoff).order_by('-created_at')
            
            print(f"\n{'='*80}")
            print(f"RECENT ORDERS (Last {days_back} days)")
            print(f"{'='*80}\n")
            
            for order in orders:
                in_zoho, invoices = check_order_in_zoho(order.order_number)
                status = "✅ Synced" if in_zoho else ("⚠️ Unknown" if in_zoho is None else "❌ Not synced")
                
                print(f"{order.order_number} - {order.created_at.strftime('%Y-%m-%d %H:%M')} - {status}")
                if in_zoho and invoices:
                    print(f"   Invoice: {invoices[0].get('invoice_number')}")
        
        elif choice == "0":
            print("\nExiting...\n")
            break
        
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    # Quick mode: if order number provided as argument
    if len(sys.argv) > 1:
        order_number = sys.argv[1]
        retry_single_order(order_number)
    else:
        main()


