#!/usr/bin/env python
"""
Check for a specific order in Zoho by reference number.
"""
import os
import sys

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.integrations.zoho_inventory import _zget
from myApp.models import Order

def check_specific_order():
    """Check for order SH-503744 in Zoho"""
    print("🔍 Checking for Order SH-503744 in Zoho")
    print("=" * 50)
    
    # First check if it exists in our local database
    try:
        local_order = Order.objects.get(order_number="SH-503744")
        print(f"✅ Found order in local database:")
        print(f"   Customer: {local_order.full_name}")
        print(f"   Date: {local_order.created_at}")
        print(f"   Total: ${local_order.grand_total}")
        print(f"   Items: {local_order.items.count()}")
        
        for item in local_order.items.all():
            print(f"     - {item.name} × {item.quantity}")
            
    except Order.DoesNotExist:
        print("❌ Order SH-503744 not found in local database")
        return
    
    # Now check in Zoho
    print(f"\n🔍 Searching for order in Zoho...")
    
    try:
        # Search for the specific order by reference number
        response = _zget("salesorders", params={"reference_number": "SH-503744"})
        
        orders = response.get("salesorders", [])
        
        if orders:
            print(f"✅ Found order in Zoho!")
            order_data = orders[0]
            print(f"   Reference: {order_data.get('reference_number')}")
            print(f"   Customer: {order_data.get('customer_name')}")
            print(f"   Date: {order_data.get('date')}")
            print(f"   Total: ${order_data.get('total')}")
            print(f"   Status: {order_data.get('status')}")
            print(f"   Sales Order ID: {order_data.get('salesorder_id')}")
        else:
            print(f"❌ Order SH-503744 NOT found in Zoho")
            print(f"   This means the order was not successfully pushed to Zoho")
            
            # Try to push it now
            print(f"\n🚀 Attempting to push order to Zoho now...")
            from myApp.integrations.zoho_inventory import push_order_to_zoho
            try:
                push_order_to_zoho(local_order)
                print(f"✅ Order successfully pushed to Zoho!")
            except Exception as e:
                print(f"❌ Failed to push order: {e}")
                
    except Exception as e:
        print(f"❌ Error checking Zoho: {e}")

if __name__ == "__main__":
    check_specific_order()

