#!/usr/bin/env python
"""
Verification Script: Zoho Inventory Deduction
Tests and verifies that inventory is being properly deducted when orders are processed.
"""

import os
import sys
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.integrations.zoho_inventory import _get_access_token, _zget
from myApp.models import Order, OrderItem

def get_item_stock(sku: str):
    """Get current stock level for an item by SKU."""
    try:
        result = _zget("items", params={"sku": sku})
        items = result.get("items", [])
        if items:
            item = items[0]
            return {
                "item_id": item.get("item_id"),
                "name": item.get("name"),
                "sku": item.get("sku"),
                "stock_on_hand": item.get("stock_on_hand", 0),
                "reorder_level": item.get("reorder_level", 0),
                "is_combo_product": item.get("is_combo_product", False),
            }
        return None
    except Exception as e:
        print(f"❌ Error fetching item {sku}: {e}")
        return None

def check_recent_orders_deduction():
    """Check if recent orders have been properly synced and inventory deducted."""
    print("=" * 80)
    print("CHECKING RECENT ORDERS FOR INVENTORY DEDUCTION")
    print("=" * 80)
    
    # Get last 5 orders
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    if not recent_orders:
        print("\n⚠️  No orders found in database.")
        return
    
    print(f"\nAnalyzing last {len(recent_orders)} orders...\n")
    
    for order in recent_orders:
        print(f"📦 Order: {order.order_number}")
        print(f"   Customer: {order.full_name}")
        print(f"   Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Status: {order.get_status_display()}")
        
        # Check each item in the order
        items = order.items.all()
        print(f"   Items ({len(items)}):")
        
        for item in items:
            product = item.product
            sku = product.sku if product.sku else "NO-SKU"
            
            # Get current Zoho stock
            zoho_item = get_item_stock(sku)
            
            if zoho_item:
                stock_status = f"{zoho_item['stock_on_hand']:.0f} units"
                if zoho_item['stock_on_hand'] < zoho_item['reorder_level']:
                    stock_status += " ⚠️ BELOW REORDER"
                
                print(f"      - {product.name}")
                print(f"        SKU: {sku}")
                print(f"        Ordered: {item.quantity} units")
                print(f"        Current Zoho Stock: {stock_status}")
                
                if zoho_item.get('is_combo_product'):
                    print(f"        Type: Bundle/Composite Item")
            else:
                print(f"      - {product.name}")
                print(f"        SKU: {sku}")
                print(f"        Ordered: {item.quantity} units")
                print(f"        ❌ NOT FOUND IN ZOHO (inventory may not be tracked)")
        
        print()

def verify_sku_matching():
    """Verify that all products have SKUs that match items in Zoho."""
    print("=" * 80)
    print("VERIFYING SKU MATCHING BETWEEN SYSTEMS")
    print("=" * 80)
    
    from myApp.models import Product
    
    products = Product.objects.all()
    print(f"\nChecking {len(products)} products in database...\n")
    
    matched = []
    missing_sku = []
    not_in_zoho = []
    
    for product in products:
        if not product.sku:
            missing_sku.append(product)
            print(f"⚠️  {product.name} - NO SKU IN DATABASE")
            continue
        
        zoho_item = get_item_stock(product.sku)
        if zoho_item:
            matched.append((product, zoho_item))
            print(f"✅ {product.name}")
            print(f"   SKU: {product.sku}")
            print(f"   Zoho Stock: {zoho_item['stock_on_hand']:.0f} units")
        else:
            not_in_zoho.append(product)
            print(f"❌ {product.name}")
            print(f"   SKU: {product.sku}")
            print(f"   NOT FOUND IN ZOHO")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Matched: {len(matched)} products")
    print(f"⚠️  Missing SKU: {len(missing_sku)} products")
    print(f"❌ Not in Zoho: {len(not_in_zoho)} products")
    
    if missing_sku:
        print(f"\n⚠️  Products without SKU:")
        for p in missing_sku:
            print(f"   - {p.name} (ID: {p.id})")
    
    if not_in_zoho:
        print(f"\n❌ Products not found in Zoho (check SKU spelling):")
        for p in not_in_zoho:
            print(f"   - {p.name} (SKU: {p.sku})")

def test_stock_lookup():
    """Test stock lookup for a few sample items."""
    print("=" * 80)
    print("TESTING ZOHO STOCK LOOKUP")
    print("=" * 80)
    
    # Sample SKUs from your inventory
    test_skus = [
        "SHARP-SHARPSHAMPOO-31",
        "SHARP-SHARPCONDITI-32",
        "SHARP-SHARPTREATME-33",
        "SHARP-FULLPACKAGE-23",
    ]
    
    print("\nTesting stock lookup for sample items...\n")
    
    for sku in test_skus:
        item = get_item_stock(sku)
        if item:
            print(f"✅ {item['name']}")
            print(f"   SKU: {sku}")
            print(f"   Stock: {item['stock_on_hand']:.0f} units")
            print(f"   Reorder Level: {item['reorder_level']:.0f}")
            if item.get('is_combo_product'):
                print(f"   Type: Bundle/Composite")
            print()
        else:
            print(f"❌ SKU not found: {sku}\n")

def simulate_deduction_check(order_number=None):
    """Simulate checking what would be deducted for a specific order."""
    print("=" * 80)
    print("SIMULATED INVENTORY DEDUCTION CHECK")
    print("=" * 80)
    
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            print(f"\n❌ Order {order_number} not found.")
            return
    else:
        # Get most recent order
        order = Order.objects.all().order_by('-created_at').first()
        if not order:
            print("\n⚠️  No orders in database.")
            return
    
    print(f"\nAnalyzing Order: {order.order_number}")
    print(f"Customer: {order.full_name}")
    print(f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("Expected Inventory Deductions:")
    print("-" * 80)
    
    total_deductions = {}
    
    for item in order.items.all():
        product = item.product
        sku = product.sku or "NO-SKU"
        qty = item.quantity
        
        # Get current stock
        zoho_item = get_item_stock(sku)
        
        if zoho_item:
            current_stock = zoho_item['stock_on_hand']
            expected_after = current_stock - qty
            
            print(f"📦 {product.name}")
            print(f"   SKU: {sku}")
            print(f"   Order Qty: {qty} units")
            print(f"   Current Stock: {current_stock:.0f} units")
            print(f"   After Deduction: {expected_after:.0f} units")
            
            if expected_after < 0:
                print(f"   ⚠️  WARNING: Would result in negative stock!")
            elif expected_after < zoho_item['reorder_level']:
                print(f"   ⚠️  WARNING: Would fall below reorder level ({zoho_item['reorder_level']:.0f})")
            
            if getattr(product, 'is_bundle', False):
                print(f"   📦 Bundle - Components will also be deducted")
            
            print()
            
            total_deductions[sku] = qty
    
    print("=" * 80)
    print(f"Total items to deduct: {len(total_deductions)}")

def check_zoho_invoices_for_order(order_number):
    """Check if an invoice exists in Zoho for a specific order."""
    print("=" * 80)
    print(f"CHECKING ZOHO INVOICES FOR ORDER: {order_number}")
    print("=" * 80)
    
    try:
        # Search for invoices by reference number
        result = _zget("invoices", params={"reference_number": order_number})
        invoices = result.get("invoices", [])
        
        if invoices:
            print(f"\n✅ Found {len(invoices)} invoice(s) for order {order_number}:\n")
            for inv in invoices:
                print(f"Invoice Number: {inv.get('invoice_number')}")
                print(f"Invoice ID: {inv.get('invoice_id')}")
                print(f"Status: {inv.get('status')}")
                print(f"Total: {inv.get('total')}")
                print(f"Date: {inv.get('date')}")
                print(f"Customer: {inv.get('customer_name')}")
                
                # Check if stock was deducted
                if inv.get('status') in ['sent', 'paid', 'overdue']:
                    print(f"✅ Inventory deduction: COMPLETED (invoice is {inv.get('status')})")
                else:
                    print(f"⚠️  Inventory deduction: May not be complete (status: {inv.get('status')})")
                print()
        else:
            print(f"\n❌ No invoice found for order {order_number}")
            print("   This could mean:")
            print("   - Zoho sync failed")
            print("   - Sync is still in progress")
            print("   - Order was created before Zoho integration")
    except Exception as e:
        print(f"❌ Error checking invoices: {e}")

def main():
    """Main verification routine."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ZOHO INVENTORY DEDUCTION VERIFICATION" + " " * 21 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    # Test connection
    print("📡 Testing Zoho connection...")
    try:
        _get_access_token()
        print("✅ Connected to Zoho successfully!\n")
    except Exception as e:
        print(f"❌ Failed to connect to Zoho: {e}")
        sys.exit(1)
    
    # Run checks
    while True:
        print("\nSelect verification option:")
        print("1. Check recent orders for deduction")
        print("2. Verify SKU matching (all products)")
        print("3. Test stock lookup for sample items")
        print("4. Simulate deduction for specific order")
        print("5. Check Zoho invoice for order number")
        print("6. Run all checks")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == "1":
            check_recent_orders_deduction()
        elif choice == "2":
            verify_sku_matching()
        elif choice == "3":
            test_stock_lookup()
        elif choice == "4":
            order_num = input("Enter order number (or press Enter for most recent): ").strip()
            simulate_deduction_check(order_num if order_num else None)
        elif choice == "5":
            order_num = input("Enter order number: ").strip()
            if order_num:
                check_zoho_invoices_for_order(order_num)
        elif choice == "6":
            test_stock_lookup()
            print("\n")
            verify_sku_matching()
            print("\n")
            check_recent_orders_deduction()
            print("\n")
            # Check invoice for most recent order
            recent_order = Order.objects.all().order_by('-created_at').first()
            if recent_order:
                check_zoho_invoices_for_order(recent_order.order_number)
        elif choice == "0":
            print("\nExiting...\n")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()


