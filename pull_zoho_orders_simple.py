#!/usr/bin/env python
"""
Pull sales orders from Zoho Inventory and import them into our database.
Filters by Reference # to identify our orders (those with our order number format).
"""

import os
import sys
import json
from decimal import Decimal
from datetime import datetime

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.db import transaction
from django.utils import timezone
from myApp.models import Order, OrderItem, Product
from myApp.integrations.zoho_inventory import _get_access_token, _zget

def fetch_all_sales_orders():
    """Fetch all sales orders from Zoho with pagination."""
    all_orders = []
    page = 1
    per_page = 200  # Max allowed by Zoho
    
    print("Fetching sales orders from Zoho...")
    
    while True:
        print(f"  Fetching page {page}...", end=" ")
        try:
            result = _zget("salesorders", params={"page": page, "per_page": per_page})
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        orders = result.get("salesorders", [])
        all_orders.extend(orders)
        print(f"Got {len(orders)} orders")
        
        # Check if there are more pages
        page_context = result.get("page_context", {})
        has_more = page_context.get("has_more_page", False)
        
        if not has_more or not orders:
            break
            
        page += 1
    
    return all_orders

def is_our_order(sales_order):
    """Check if this sales order belongs to us by looking at reference_number."""
    reference = sales_order.get("reference_number", "")
    
    # Our order numbers look like "SH-123456"
    if reference and reference.startswith("SH-") and len(reference) == 9:
        return True
    
    # Also check salesorder_number in case it's stored there
    so_number = sales_order.get("salesorder_number", "")
    if so_number and so_number.startswith("SH-") and len(so_number) == 9:
        return True
    
    return False

def find_or_create_product(item_data):
    """Find existing product by SKU or create a placeholder."""
    sku = item_data.get("sku")
    name = item_data.get("name", "Unknown Product")
    
    if sku:
        try:
            product = Product.objects.get(sku=sku)
            return product
        except Product.DoesNotExist:
            pass
    
    # Create a placeholder product
    product = Product(
        name=name,
        sku=sku or f"ZOHO-{item_data.get('item_id', 'UNKNOWN')}",
        price=Decimal(str(item_data.get("rate", 0))),
        is_active=True
    )
    product.save()
    print(f"    Created product: {product.name} (SKU: {product.sku})")
    return product

def parse_address(address_data):
    """Parse Zoho address format into our format."""
    if not address_data:
        return {}
    
    return {
        "address_line1": address_data.get("address", ""),
        "city": address_data.get("city", ""),
        "state": address_data.get("state", ""),
        "postal_code": address_data.get("zip", ""),
        "country": address_data.get("country", ""),
    }

def create_order_from_zoho(so_data):
    """Create an Order and OrderItems from Zoho sales order data."""
    order_number = so_data.get("reference_number") or so_data.get("salesorder_number")
    
    # Check if order already exists
    if Order.objects.filter(order_number=order_number).exists():
        print(f"    Order {order_number} already exists, skipping")
        return None
    
    # Parse customer info
    customer = so_data.get("customer", {})
    customer_name = customer.get("customer_name", "Unknown Customer")
    
    # Parse addresses
    shipping_addr = parse_address(so_data.get("shipping_address", {}))
    billing_addr = parse_address(so_data.get("billing_address", {}))
    
    # Use shipping address as primary address
    primary_addr = shipping_addr or billing_addr
    
    # Parse dates
    so_date = so_data.get("date", "")
    if so_date:
        try:
            created_at = datetime.strptime(so_date, "%Y-%m-%d").replace(tzinfo=timezone.get_current_timezone())
        except:
            created_at = timezone.now()
    else:
        created_at = timezone.now()
    
    # Create the order
    order = Order(
        order_number=order_number,
        created_at=created_at,
        full_name=customer_name,
        phone=customer.get("phone", ""),
        email=customer.get("email", ""),
        address_line1=primary_addr.get("address_line1", ""),
        city=primary_addr.get("city", ""),
        province=primary_addr.get("state", ""),
        zip_code=primary_addr.get("postal_code", ""),
        country=primary_addr.get("country", ""),
        shipping_address=shipping_addr,
        shipping_address_text=f"{primary_addr.get('address_line1', '')}, {primary_addr.get('city', '')}, {primary_addr.get('state', '')} {primary_addr.get('postal_code', '')}".strip(),
        payment_method="cod",  # Default assumption
        subtotal=Decimal(str(so_data.get("sub_total", 0))),
        shipping_cost=Decimal(str(so_data.get("shipping_charge", 0))),
        discount_total=Decimal(str(so_data.get("discount", 0))),
        grand_total=Decimal(str(so_data.get("total", 0))),
        status="0",  # Created status
        notes=f"Imported from Zoho on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
        # Store Zoho IDs for reference
        zoho_data={
            "salesorder_id": so_data.get("salesorder_id"),
            "contact_id": customer.get("customer_id"),
            "synced_at": timezone.now().isoformat(),
            "import_source": "zoho_pull"
        }
    )
    
    # Save order first
    order.save()
    print(f"    Created order: {order.order_number}")
    
    # Create order items
    line_items = so_data.get("line_items", [])
    for item_data in line_items:
        product = find_or_create_product(item_data)
        
        order_item = OrderItem(
            order=order,
            product=product,
            name=item_data.get("name", product.name),
            unit_price=Decimal(str(item_data.get("rate", 0))),
            quantity=int(item_data.get("quantity", 1)),
            line_total=Decimal(str(item_data.get("quantity", 1))) * Decimal(str(item_data.get("rate", 0)))
        )
        order_item.save()
    
    print(f"    Added {len(line_items)} items to order")
    return order

def main():
    print("=" * 80)
    print("PULL ALL ZOHO SALES ORDERS")
    print("=" * 80)
    
    try:
        # Get access token
        print("\nConnecting to Zoho...")
        _get_access_token()
        print("Connected successfully!\n")
        
        # Fetch all sales orders
        all_orders = fetch_all_sales_orders()
        print(f"\nTotal sales orders found: {len(all_orders)}")
        
        # Filter our orders
        our_orders = [so for so in all_orders if is_our_order(so)]
        print(f"Our orders (with Reference #): {len(our_orders)}")
        
        if not our_orders:
            print("\nNo orders with our Reference # format found!")
            return
        
        print(f"\nImporting {len(our_orders)} orders...")
        print("-" * 60)
        
        imported_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for so_data in our_orders:
                order_number = so_data.get("reference_number") or so_data.get("salesorder_number")
                print(f"\nProcessing: {order_number}")
                
                try:
                    order = create_order_from_zoho(so_data)
                    if order:
                        imported_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    print(f"    Error importing {order_number}: {e}")
                    skipped_count += 1
                    # Continue with other orders
        
        print("\n" + "=" * 60)
        print(f"IMPORT SUMMARY:")
        print(f"   Total orders found: {len(all_orders)}")
        print(f"   Our orders (with Reference #): {len(our_orders)}")
        print(f"   Successfully imported: {imported_count}")
        print(f"   Skipped (already exist): {skipped_count}")
        print("=" * 60)
        
        # Show some examples of imported orders
        if imported_count > 0:
            print(f"\nRECENTLY IMPORTED ORDERS:")
            recent_orders = Order.objects.filter(
                zoho_data__import_source="zoho_pull"
            ).order_by('-created_at')[:5]
            
            for order in recent_orders:
                print(f"   {order.order_number} - {order.full_name} - ${order.grand_total}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
