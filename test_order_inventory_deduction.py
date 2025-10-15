#!/usr/bin/env python
"""Test that creating a Zoho Sales Order + Invoice properly deducts inventory."""

import os
import sys
import time
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.utils import timezone
from myApp.models import Order, OrderItem, Product
from myApp.integrations.zoho_inventory import push_order_to_zoho, _get_access_token, _zget

def get_zoho_stock(sku):
    """Get current stock level from Zoho by SKU."""
    try:
        result = _zget("items", params={"sku": sku})
        items = result.get("items", [])
        if items:
            return items[0].get("stock_on_hand", 0)
        return None
    except Exception as e:
        print(f"Error fetching stock for {sku}: {e}")
        return None

def create_test_order():
    """Create a test order with both regular items and bundle items."""
    
    # Find products - use actual products that exist in Zoho
    try:
        # Get a regular item that exists in Zoho
        regular_product = Product.objects.filter(
            sku="SHARP-SHARPCONDITI-32", is_bundle=False
        ).first()
        
        # Get a bundle item that exists in Zoho
        bundle_product = Product.objects.filter(
            sku="SHARP-CONDITIONERO-40", is_bundle=True
        ).first()
        
        if not regular_product:
            print("❌ No regular products found in database!")
            return None
            
        if not bundle_product:
            print("❌ No bundle products found in database!")
            return None
        
        print(f"\n📦 Selected products for test order:")
        print(f"   Regular: {regular_product.name} ({regular_product.sku})")
        print(f"   Bundle:  {bundle_product.name} ({bundle_product.sku})")
        
        # Create test order
        order = Order.objects.create(
            order_number=f"TEST-ORDER-{int(time.time())}",
            full_name="Test Customer - Inventory Check",
            email="test@example.com",
            phone="+962791234567",
            address_line1="Test Address, Amman, Jordan",
            country="JO",
            shipping_address_text="Test Address, Amman, Jordan",
            payment_method="Online",
            subtotal=Decimal("50.00"),
            shipping_cost=Decimal("0.00"),
            grand_total=Decimal("50.00"),
            status="0",
            created_at=timezone.now()
        )
        
        # Add order items
        OrderItem.objects.create(
            order=order,
            product=regular_product,
            name=regular_product.name,
            quantity=1,
            unit_price=regular_product.price,
            line_total=regular_product.price * 1
        )
        
        OrderItem.objects.create(
            order=order,
            product=bundle_product,
            name=bundle_product.name,
            quantity=1,
            unit_price=bundle_product.price,
            line_total=bundle_product.price * 1
        )
        
        print(f"\n✅ Test order created: {order.order_number}")
        return order
        
    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 80)
    print("ZOHO INVENTORY DEDUCTION TEST - Sales Order + Invoice Flow")
    print("=" * 80)
    
    try:
        # Connect to Zoho
        print("\n📡 Connecting to Zoho Inventory...")
        _get_access_token()
        print("✅ Connected successfully!")
        
        # Create test order
        print("\n" + "=" * 80)
        print("STEP 1: Creating test order in local database")
        print("=" * 80)
        
        order = create_test_order()
        if not order:
            print("❌ Failed to create test order")
            return
        
        # Get inventory levels BEFORE
        print("\n" + "=" * 80)
        print("STEP 2: Recording inventory levels BEFORE order")
        print("=" * 80)
        
        stock_before = {}
        for item in order.items.all():
            product = item.product
            sku = product.sku
            if sku:
                stock = get_zoho_stock(sku)
                stock_before[sku] = stock
                print(f"   {product.name} ({sku}): {stock} units")
                
                # If it's a bundle, also check components
                if product.is_bundle:
                    print(f"      └─ Bundle components:")
                    from myApp.models import ProductComponent
                    for link in ProductComponent.objects.filter(parent=product).select_related("component"):
                        comp = link.component
                        comp_stock = get_zoho_stock(comp.sku) if comp.sku else None
                        stock_before[comp.sku] = comp_stock
                        print(f"         - {link.quantity}x {comp.name} ({comp.sku}): {comp_stock} units")
        
        # Push order to Zoho
        print("\n" + "=" * 80)
        print("STEP 3: Pushing order to Zoho (SO + Invoice)")
        print("=" * 80)
        
        print(f"\n🚀 Creating Sales Order and Invoice for {order.order_number}...")
        push_order_to_zoho(order)
        print(f"✅ Order pushed to Zoho successfully!")
        
        # Wait a moment for Zoho to process
        print("\n⏳ Waiting 3 seconds for Zoho to process...")
        time.sleep(3)
        
        # Get inventory levels AFTER
        print("\n" + "=" * 80)
        print("STEP 4: Checking inventory levels AFTER order")
        print("=" * 80)
        
        stock_after = {}
        for item in order.items.all():
            product = item.product
            sku = product.sku
            if sku:
                stock = get_zoho_stock(sku)
                stock_after[sku] = stock
                before = stock_before.get(sku, 0)
                difference = (stock - before) if (stock is not None and before is not None) else None
                
                print(f"   {product.name} ({sku}):")
                print(f"      Before: {before} units")
                print(f"      After:  {stock} units")
                if difference is not None:
                    print(f"      Change: {difference:+.0f} units")
                
                # If it's a bundle, also check components
                if product.is_bundle:
                    print(f"      └─ Bundle components:")
                    from myApp.models import ProductComponent
                    for link in ProductComponent.objects.filter(parent=product).select_related("component"):
                        comp = link.component
                        comp_stock = get_zoho_stock(comp.sku) if comp.sku else None
                        stock_after[comp.sku] = comp_stock
                        comp_before = stock_before.get(comp.sku, 0)
                        comp_diff = (comp_stock - comp_before) if (comp_stock is not None and comp_before is not None) else None
                        
                        print(f"         - {link.quantity}x {comp.name} ({comp.sku}):")
                        print(f"           Before: {comp_before} units")
                        print(f"           After:  {comp_stock} units")
                        if comp_diff is not None:
                            print(f"           Change: {comp_diff:+.0f} units (Expected: {-int(link.quantity)})")
        
        # Summary
        print("\n" + "=" * 80)
        print("ANALYSIS & RESULTS")
        print("=" * 80)
        
        all_deducted = True
        for sku, before in stock_before.items():
            after = stock_after.get(sku)
            if before is not None and after is not None:
                if after < before:
                    print(f"✅ {sku}: Inventory was deducted ({before} → {after})")
                elif after == before:
                    print(f"⚠️  {sku}: No change in inventory ({before} → {after})")
                    all_deducted = False
                else:
                    print(f"❌ {sku}: Inventory INCREASED? ({before} → {after})")
                    all_deducted = False
        
        print("\n" + "=" * 80)
        if all_deducted:
            print("🎉 SUCCESS! All inventory was properly deducted!")
            print("   ✅ Sales Order → Invoice conversion is working correctly")
            print("   ✅ Bundle/Combo items are deducting component inventory")
        else:
            print("⚠️  WARNING! Some inventory was NOT deducted!")
            print("   Check the results above to see which items didn't deduct")
        print("=" * 80)
        
        # Cleanup option
        print(f"\n📝 Test order created: {order.order_number}")
        print(f"   You can find this order in Zoho Inventory")
        print(f"   Local order ID: {order.id}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

