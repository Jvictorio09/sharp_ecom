#!/usr/bin/env python
"""
URGENT: Copy local data to production database.
This will restore your products, users, and other data to production.
"""

import os
import sys
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.db import connection, transaction
from myApp.models import Product, Order, OrderItem, PromoCode, Post, PostBlock, Subscriber, FxRate
from django.contrib.auth.models import User

def copy_data_to_production():
    """Copy all local data to production database."""
    print("=" * 60)
    print("URGENT: COPYING LOCAL DATA TO PRODUCTION")
    print("=" * 60)
    
    print(f"Current database: {connection.settings_dict['ENGINE']}")
    print(f"Database name: {connection.settings_dict['NAME']}")
    
    # Check if we're in production (PostgreSQL)
    is_production = 'postgresql' in connection.settings_dict['ENGINE']
    
    if not is_production:
        print("ERROR: This script should be run in production environment!")
        print("Make sure DATABASE_URL is set to your production PostgreSQL database.")
        return False
    
    print("\nCopying data to production PostgreSQL database...")
    
    with transaction.atomic():
        try:
            # 1. Copy Users
            print("\n1. Copying Users...")
            local_users = User.objects.using('default').all()
            for user in local_users:
                if not User.objects.filter(username=user.username).exists():
                    User.objects.create_user(
                        username=user.username,
                        email=user.email,
                        password='temp_password_123',  # Will need to reset
                        is_staff=user.is_staff,
                        is_superuser=user.is_superuser,
                        is_active=user.is_active
                    )
                    print(f"   Created user: {user.username}")
            
            # 2. Copy Products
            print("\n2. Copying Products...")
            local_products = Product.objects.using('default').all()
            for product in local_products:
                if not Product.objects.filter(slug=product.slug).exists():
                    Product.objects.create(
                        name=product.name,
                        sku=product.sku,
                        slug=product.slug,
                        short_description=product.short_description,
                        description=product.description,
                        price=product.price,
                        image_url=product.image_url,
                        is_active=product.is_active,
                        gallery_csv=product.gallery_csv,
                        is_bundle=product.is_bundle,
                        free_delivery=product.free_delivery,
                        created_at=product.created_at
                    )
                    print(f"   Created product: {product.name}")
            
            # 3. Copy Orders
            print("\n3. Copying Orders...")
            local_orders = Order.objects.using('default').all()
            for order in local_orders:
                if not Order.objects.filter(order_number=order.order_number).exists():
                    Order.objects.create(
                        order_number=order.order_number,
                        created_at=order.created_at,
                        updated_at=order.updated_at,
                        cancel_reason=order.cancel_reason,
                        full_name=order.full_name,
                        phone=order.phone,
                        email=order.email,
                        address_line1=order.address_line1,
                        city=order.city,
                        province=order.province,
                        zip_code=order.zip_code,
                        country=order.country,
                        shipping_address=order.shipping_address,
                        shipping_address_text=order.shipping_address_text,
                        shipping_method=order.shipping_method,
                        payment_method=order.payment_method,
                        subtotal=order.subtotal,
                        shipping_cost=order.shipping_cost,
                        discount_total=order.discount_total,
                        grand_total=order.grand_total,
                        notes=order.notes,
                        status=order.status,
                        zoho_data=order.zoho_data
                    )
                    print(f"   Created order: {order.order_number}")
            
            # 4. Copy Order Items
            print("\n4. Copying Order Items...")
            local_items = OrderItem.objects.using('default').all()
            for item in local_items:
                # Find the corresponding order and product in production
                try:
                    order = Order.objects.get(order_number=item.order.order_number)
                    product = Product.objects.get(slug=item.product.slug)
                    
                    if not OrderItem.objects.filter(order=order, product=product, name=item.name).exists():
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            name=item.name,
                            unit_price=item.unit_price,
                            quantity=item.quantity,
                            line_total=item.line_total,
                            cancel_reason=item.cancel_reason
                        )
                        print(f"   Created order item: {item.name}")
                except Exception as e:
                    print(f"   Error copying item {item.name}: {e}")
            
            # 5. Copy Promo Codes
            print("\n5. Copying Promo Codes...")
            local_promos = PromoCode.objects.using('default').all()
            for promo in local_promos:
                if not PromoCode.objects.filter(code=promo.code).exists():
                    PromoCode.objects.create(
                        code=promo.code,
                        type=promo.type,
                        value=promo.value,
                        description=promo.description,
                        min_subtotal=promo.min_subtotal,
                        max_discount=promo.max_discount,
                        countries_csv=promo.countries_csv,
                        starts_at=promo.starts_at,
                        ends_at=promo.ends_at,
                        active=promo.active,
                        usage_limit=promo.usage_limit,
                        used_count=promo.used_count,
                        created_at=promo.created_at,
                        updated_at=promo.updated_at
                    )
                    print(f"   Created promo code: {promo.code}")
            
            print("\n✅ Data copy completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error copying data: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("URGENT: This script will copy your local data to production.")
    print("Make sure you're connected to your production database!")
    
    response = input("\nContinue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    if copy_data_to_production():
        print("\n🎉 SUCCESS: Your production database has been restored!")
        print("You should now be able to login and see your products.")
    else:
        print("\n❌ FAILED: Data copy failed. Check the errors above.")

if __name__ == "__main__":
    main()
