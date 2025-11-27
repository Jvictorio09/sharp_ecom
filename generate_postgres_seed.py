#!/usr/bin/env python
"""
Clean PostgreSQL Seed File Generator
Exports all data from SQLite (db.sqlite3) to a PostgreSQL-compatible seed file.

This script reads from your current SQLite database and creates a seed file
that you can use to populate your PostgreSQL database.

Run this script to generate seed_postgres.py - then run that file on your PostgreSQL database.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.conf import settings
from django.db import connection
from django.contrib.auth.models import User
from myApp.models import Product, Order, OrderItem, PromoCode, Post, PostBlock, Subscriber, FxRate, ProductComponent

def generate_postgres_seed():
    """Generate a clean PostgreSQL seed file with all data from SQLite."""
    
    print("=" * 70)
    print("PostgreSQL Seed File Generator")
    print("Reading from SQLite database (db.sqlite3)")
    print("=" * 70)
    print()
    
    # Verify we're reading from SQLite
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    
    if 'sqlite' not in db_engine:
        print("⚠️  WARNING: Not using SQLite! Current database engine:", db_engine)
        print("   This script is designed to export from SQLite.")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("   Aborted.")
            return
    else:
        # Check if SQLite file exists
        sqlite_path = Path(db_name)
        if not sqlite_path.exists():
            print(f"❌ ERROR: SQLite database file not found: {sqlite_path}")
            print("   Please make sure db.sqlite3 exists in the project root.")
            return
        print(f"✅ Found SQLite database: {sqlite_path}")
        print(f"   File size: {sqlite_path.stat().st_size / 1024:.2f} KB")
        print()
    
    all_data = {}
    
    # 1. Export Products (with images) - FILTER: Only Cloudinary images
    print("📦 Exporting Products (Cloudinary images only)...")
    try:
        products = Product.objects.all().order_by('name')
        all_data['products'] = []
        for product in products:
            # Filter: Only keep products with Cloudinary images
            image_url = product.image_url or ''
            gallery_csv = product.gallery_csv or ''
            has_cloudinary = 'res.cloudinary.com' in str(image_url) or 'res.cloudinary.com' in str(gallery_csv)
            
            if not has_cloudinary:
                continue  # Skip products without Cloudinary images
            product_data = {
                'name': product.name,
                'sku': product.sku or '',
                'slug': product.slug,
                'short_description': product.short_description,
                'description': product.description,
                'price': float(product.price),
                'image_url': product.image_url or '',
                'is_active': product.is_active,
                'gallery_csv': product.gallery_csv or '',
                'is_bundle': product.is_bundle,
                'free_delivery': product.free_delivery,
                'created_at': product.created_at.isoformat(),
            }
            all_data['products'].append(product_data)
        print(f"   ✅ Exported {len(all_data['products'])} products")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['products'] = []
    
    # 2. Export Product Components (bundle relationships)
    print("🔗 Exporting Product Components...")
    try:
        components = ProductComponent.objects.all().select_related('parent', 'component')
        all_data['product_components'] = []
        for comp in components:
            all_data['product_components'].append({
                'parent_name': comp.parent.name,
                'component_name': comp.component.name,
                'quantity': comp.quantity,
            })
        print(f"   ✅ Exported {len(all_data['product_components'])} product components")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['product_components'] = []
    
    # 3. Export Orders (all past orders)
    print("📋 Exporting Orders...")
    try:
        orders = Order.objects.all().order_by('-created_at')
        all_data['orders'] = []
        for order in orders:
            order_data = {
                'order_number': order.order_number,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat(),
                'cancel_reason': order.cancel_reason or '',
                'full_name': order.full_name,
                'phone': order.phone,
                'email': order.email or '',
                'address_line1': order.address_line1,
                'city': order.city or '',
                'province': order.province or '',
                'zip_code': order.zip_code or '',
                'country': order.country or '',
                'shipping_address': order.shipping_address or {},
                'shipping_address_text': order.shipping_address_text or '',
                'shipping_method': order.shipping_method,
                'payment_method': order.payment_method,
                'subtotal': float(order.subtotal),
                'shipping_cost': float(order.shipping_cost),
                'discount_total': float(order.discount_total),
                'grand_total': float(order.grand_total),
                'notes': order.notes or '',
                'status': order.status,
                'zoho_data': order.zoho_data or {},
            }
            # Add promo fields if they exist
            if hasattr(order, 'promo_code'):
                order_data['promo_code'] = order.promo_code or ''
            if hasattr(order, 'promo_label'):
                order_data['promo_label'] = order.promo_label or ''
            all_data['orders'].append(order_data)
        print(f"   ✅ Exported {len(all_data['orders'])} orders")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['orders'] = []
    
    # 4. Export Order Items
    print("🛒 Exporting Order Items...")
    try:
        order_items = OrderItem.objects.all().select_related('order', 'product')
        all_data['order_items'] = []
        for item in order_items:
            all_data['order_items'].append({
                'order_number': item.order.order_number,
                'product_name': item.product.name,
                'name': item.name,
                'unit_price': float(item.unit_price),
                'quantity': item.quantity,
                'line_total': float(item.line_total),
                'cancel_reason': item.cancel_reason or '',
            })
        print(f"   ✅ Exported {len(all_data['order_items'])} order items")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['order_items'] = []
    
    # 5. Export Promo Codes
    print("🎫 Exporting Promo Codes...")
    try:
        promos = PromoCode.objects.all()
        all_data['promo_codes'] = []
        for promo in promos:
            all_data['promo_codes'].append({
                'code': promo.code,
                'type': promo.type,
                'value': float(promo.value),
                'description': promo.description or '',
                'min_subtotal': float(promo.min_subtotal),
                'max_discount': float(promo.max_discount) if promo.max_discount else None,
                'countries_csv': promo.countries_csv or '',
                'starts_at': promo.starts_at.isoformat() if promo.starts_at else None,
                'ends_at': promo.ends_at.isoformat() if promo.ends_at else None,
                'active': promo.active,
                'usage_limit': promo.usage_limit,
                'used_count': promo.used_count,
                'created_at': promo.created_at.isoformat(),
                'updated_at': promo.updated_at.isoformat(),
            })
        print(f"   ✅ Exported {len(all_data['promo_codes'])} promo codes")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['promo_codes'] = []
    
    # 6. Export Blog Posts (with images)
    print("📝 Exporting Blog Posts...")
    try:
        posts = Post.objects.all()
        all_data['posts'] = []
        for post in posts:
            post_data = {
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt or '',
                'cover_image_url': post.cover_image_url or '',
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'author_name': post.author_name,
            }
            # Include local image path if exists
            if post.cover_image:
                post_data['cover_image'] = str(post.cover_image)
            all_data['posts'].append(post_data)
        print(f"   ✅ Exported {len(all_data['posts'])} blog posts")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['posts'] = []
    
    # 7. Export Post Blocks (with images)
    print("📄 Exporting Post Blocks...")
    try:
        blocks = PostBlock.objects.all().select_related('post')
        all_data['post_blocks'] = []
        for block in blocks:
            block_data = {
                'post_slug': block.post.slug,
                'order': block.order,
                'kind': block.kind,
                'text': block.text or '',
                'level': block.level or '',
                'image1_url': block.image1_url or '',
                'image2_url': block.image2_url or '',
                'caption': block.caption or '',
                'prod_query': block.prod_query or '',
            }
            # Include local image paths if they exist
            if block.image1:
                block_data['image1'] = str(block.image1)
            if block.image2:
                block_data['image2'] = str(block.image2)
            all_data['post_blocks'].append(block_data)
        print(f"   ✅ Exported {len(all_data['post_blocks'])} post blocks")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['post_blocks'] = []
    
    # 8. Export FX Rates
    print("💱 Exporting FX Rates...")
    try:
        fx_rates = FxRate.objects.all()
        all_data['fx_rates'] = []
        for fx in fx_rates:
            all_data['fx_rates'].append({
                'base': fx.base,
                'quote': fx.quote,
                'rate': float(fx.rate),
                'updated_at': fx.updated_at.isoformat(),
            })
        print(f"   ✅ Exported {len(all_data['fx_rates'])} FX rates")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_data['fx_rates'] = []
    
    # Generate the seed file
    print()
    print("📝 Generating PostgreSQL seed file...")
    
    # Format data for the seed file
    products_str = json.dumps(all_data['products'], indent=4, ensure_ascii=False)
    components_str = json.dumps(all_data['product_components'], indent=4, ensure_ascii=False)
    orders_str = json.dumps(all_data['orders'], indent=4, ensure_ascii=False)
    order_items_str = json.dumps(all_data['order_items'], indent=4, ensure_ascii=False)
    promos_str = json.dumps(all_data['promo_codes'], indent=4, ensure_ascii=False)
    posts_str = json.dumps(all_data['posts'], indent=4, ensure_ascii=False)
    blocks_str = json.dumps(all_data['post_blocks'], indent=4, ensure_ascii=False)
    fx_rates_str = json.dumps(all_data['fx_rates'], indent=4, ensure_ascii=False)
    
    seed_content = f'''#!/usr/bin/env python
"""
PostgreSQL Seed File
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file contains all your data ready to be imported into PostgreSQL.
Run this file on your PostgreSQL database to seed it with all your data.

Usage:
    python seed_postgres.py

Or from Django shell:
    python manage.py shell
    >>> exec(open('seed_postgres.py').read())
    >>> seed_database()
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from myApp.models import (
    Product, Order, OrderItem, PromoCode, Post, PostBlock, 
    Subscriber, FxRate, ProductComponent
)

# ============================================================================
# DATA DEFINITIONS
# ============================================================================

PRODUCTS_DATA = {products_str}

PRODUCT_COMPONENTS_DATA = {components_str}

ORDERS_DATA = {orders_str}

ORDER_ITEMS_DATA = {order_items_str}

PROMO_CODES_DATA = {promos_str}

POSTS_DATA = {posts_str}

POST_BLOCKS_DATA = {blocks_str}

FX_RATES_DATA = {fx_rates_str}

# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

@transaction.atomic
def seed_database():
    """
    Seed the PostgreSQL database with all exported data.
    This function is idempotent - safe to run multiple times.
    """
    print("=" * 70)
    print("🌱 Seeding PostgreSQL Database")
    print("=" * 70)
    print()
    
    # 1. Create Products
    print("📦 Creating Products...")
    product_map = {{}}
    for product_data in PRODUCTS_DATA:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults={{
                'sku': product_data['sku'] or None,
                'slug': product_data['slug'],
                'short_description': product_data['short_description'],
                'description': product_data['description'],
                'price': Decimal(str(product_data['price'])),
                'image_url': product_data['image_url'] or None,
                'is_active': product_data['is_active'],
                'gallery_csv': product_data['gallery_csv'],
                'is_bundle': product_data['is_bundle'],
                'free_delivery': product_data['free_delivery'],
            }}
        )
        product_map[product_data['name']] = product
        if created:
            print(f"   ✅ Created: {{product.name}}")
        else:
            print(f"   ℹ️  Exists: {{product.name}}")
    print(f"   Total: {{len(product_map)}} products\\n")
    
    # 2. Create Product Components
    print("🔗 Creating Product Components...")
    components_created = 0
    for comp_data in PRODUCT_COMPONENTS_DATA:
        try:
            parent = product_map.get(comp_data['parent_name'])
            component = product_map.get(comp_data['component_name'])
            
            if not parent or not component:
                print(f"   ⚠️  Skipping: {{comp_data['parent_name']}} → {{comp_data['component_name']}} (product not found)")
                continue
            
            comp, created = ProductComponent.objects.get_or_create(
                parent=parent,
                component=component,
                defaults={{'quantity': comp_data['quantity']}}
            )
            if created:
                components_created += 1
        except Exception as e:
            print(f"   ⚠️  Error creating component: {{e}}")
    print(f"   Created: {{components_created}} components\\n")
    
    # 3. Create Promo Codes
    print("🎫 Creating Promo Codes...")
    for promo_data in PROMO_CODES_DATA:
        promo, created = PromoCode.objects.get_or_create(
            code=promo_data['code'],
            defaults={{
                'type': promo_data['type'],
                'value': Decimal(str(promo_data['value'])),
                'description': promo_data['description'],
                'min_subtotal': Decimal(str(promo_data['min_subtotal'])),
                'max_discount': Decimal(str(promo_data['max_discount'])) if promo_data['max_discount'] else None,
                'countries_csv': promo_data['countries_csv'],
                'starts_at': datetime.fromisoformat(promo_data['starts_at']) if promo_data['starts_at'] else None,
                'ends_at': datetime.fromisoformat(promo_data['ends_at']) if promo_data['ends_at'] else None,
                'active': promo_data['active'],
                'usage_limit': promo_data['usage_limit'],
                'used_count': promo_data['used_count'],
            }}
        )
        if created:
            print(f"   ✅ Created: {{promo.code}}")
        else:
            print(f"   ℹ️  Exists: {{promo.code}}")
    print()
    
    # 4. Create Orders
    print("📋 Creating Orders...")
    order_map = {{}}
    for order_data in ORDERS_DATA:
        order, created = Order.objects.get_or_create(
            order_number=order_data['order_number'],
            defaults={{
                'created_at': datetime.fromisoformat(order_data['created_at']),
                'updated_at': datetime.fromisoformat(order_data['updated_at']),
                'cancel_reason': order_data['cancel_reason'],
                'full_name': order_data['full_name'],
                'phone': order_data['phone'],
                'email': order_data['email'] or '',
                'address_line1': order_data['address_line1'],
                'city': order_data['city'],
                'province': order_data['province'],
                'zip_code': order_data['zip_code'],
                'country': order_data['country'],
                'shipping_address': order_data['shipping_address'],
                'shipping_address_text': order_data['shipping_address_text'],
                'shipping_method': order_data['shipping_method'],
                'payment_method': order_data['payment_method'],
                'subtotal': Decimal(str(order_data['subtotal'])),
                'shipping_cost': Decimal(str(order_data['shipping_cost'])),
                'discount_total': Decimal(str(order_data['discount_total'])),
                'grand_total': Decimal(str(order_data['grand_total'])),
                'notes': order_data['notes'],
                'status': order_data['status'],
                'zoho_data': order_data['zoho_data'],
                'promo_code': order_data.get('promo_code') or None,
                'promo_label': order_data.get('promo_label') or '',
            }}
        )
        order_map[order_data['order_number']] = order
        if created:
            print(f"   ✅ Created: {{order.order_number}}")
        else:
            print(f"   ℹ️  Exists: {{order.order_number}}")
    print(f"   Total: {{len(order_map)}} orders\\n")
    
    # 5. Create Order Items
    print("🛒 Creating Order Items...")
    items_created = 0
    for item_data in ORDER_ITEMS_DATA:
        try:
            order = order_map.get(item_data['order_number'])
            product = product_map.get(item_data['product_name'])
            
            if not order or not product:
                print(f"   ⚠️  Skipping: {{item_data['name']}} (order/product not found)")
                continue
            
            item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                name=item_data['name'],
                defaults={{
                    'unit_price': Decimal(str(item_data['unit_price'])),
                    'quantity': item_data['quantity'],
                    'line_total': Decimal(str(item_data['line_total'])),
                    'cancel_reason': item_data['cancel_reason'],
                }}
            )
            if created:
                items_created += 1
        except Exception as e:
            print(f"   ⚠️  Error creating order item: {{e}}")
    print(f"   Created: {{items_created}} order items\\n")
    
    # 6. Create Blog Posts
    print("📝 Creating Blog Posts...")
    post_map = {{}}
    for post_data in POSTS_DATA:
        post, created = Post.objects.get_or_create(
            slug=post_data['slug'],
            defaults={{
                'title': post_data['title'],
                'excerpt': post_data['excerpt'],
                'cover_image_url': post_data['cover_image_url'],
                'published_at': datetime.fromisoformat(post_data['published_at']) if post_data['published_at'] else None,
                'author_name': post_data['author_name'],
            }}
        )
        post_map[post_data['slug']] = post
        if created:
            print(f"   ✅ Created: {{post.title}}")
        else:
            print(f"   ℹ️  Exists: {{post.title}}")
    print()
    
    # 7. Create Post Blocks
    print("📄 Creating Post Blocks...")
    blocks_created = 0
    for block_data in POST_BLOCKS_DATA:
        try:
            post = post_map.get(block_data['post_slug'])
            if not post:
                print(f"   ⚠️  Skipping block (post not found: {{block_data['post_slug']}})")
                continue
            
            block, created = PostBlock.objects.get_or_create(
                post=post,
                order=block_data['order'],
                defaults={{
                    'kind': block_data['kind'],
                    'text': block_data['text'],
                    'level': block_data['level'],
                    'image1_url': block_data['image1_url'],
                    'image2_url': block_data['image2_url'],
                    'caption': block_data['caption'],
                    'prod_query': block_data['prod_query'],
                }}
            )
            if created:
                blocks_created += 1
        except Exception as e:
            print(f"   ⚠️  Error creating post block: {{e}}")
    print(f"   Created: {{blocks_created}} post blocks\\n")
    
    # 8. Create FX Rates
    print("💱 Creating FX Rates...")
    for fx_data in FX_RATES_DATA:
        fx, created = FxRate.objects.get_or_create(
            base=fx_data['base'],
            quote=fx_data['quote'],
            defaults={{
                'rate': Decimal(str(fx_data['rate'])),
            }}
        )
        if created:
            print(f"   ✅ Created: {{fx.base}}/{{fx.quote}}")
        else:
            print(f"   ℹ️  Exists: {{fx.base}}/{{fx.quote}}")
    print()
    
    # Summary
    print("=" * 70)
    print("🎉 Seeding Complete!")
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"   Products: {{Product.objects.count()}}")
    print(f"   Product Components: {{ProductComponent.objects.count()}}")
    print(f"   Orders: {{Order.objects.count()}}")
    print(f"   Order Items: {{OrderItem.objects.count()}}")
    print(f"   Promo Codes: {{PromoCode.objects.count()}}")
    print(f"   Blog Posts: {{Post.objects.count()}}")
    print(f"   Post Blocks: {{PostBlock.objects.count()}}")
    print(f"   FX Rates: {{FxRate.objects.count()}}")
    print("=" * 70)


if __name__ == "__main__":
    seed_database()
'''
    
    # Write the seed file
    output_file = 'seed_postgres.py'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(seed_content)
    
    print(f"✅ Seed file created: {output_file}")
    print()
    
    # Summary
    print("=" * 70)
    print("📊 EXPORT SUMMARY")
    print("=" * 70)
    print(f"   Source: SQLite (db.sqlite3)")
    print(f"   Products: {len(all_data['products'])}")
    print(f"   Product Components: {len(all_data['product_components'])}")
    print(f"   Orders: {len(all_data['orders'])}")
    print(f"   Order Items: {len(all_data['order_items'])}")
    print(f"   Promo Codes: {len(all_data['promo_codes'])}")
    print(f"   Blog Posts: {len(all_data['posts'])}")
    print(f"   Post Blocks: {len(all_data['post_blocks'])}")
    print(f"   FX Rates: {len(all_data['fx_rates'])}")
    print(f"   TOTAL RECORDS: {sum(len(data) for data in all_data.values())}")
    print("=" * 70)
    print()
    print("✅ Successfully extracted all data from SQLite!")
    print()
    print("📝 NEXT STEPS - Migrate to PostgreSQL:")
    print("   1. Review the generated file: seed_postgres.py")
    print("   2. Update settings.py to use PostgreSQL database")
    print("   3. Run migrations on PostgreSQL: python manage.py migrate")
    print("   4. Run the seed file: python seed_postgres.py")
    print("   5. Verify all data was imported correctly")
    print("   6. Once verified, you can delete db.sqlite3")
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("   • All images are stored as URLs (Cloudinary) - no file copying needed")
    print("   • The seed file is idempotent (safe to run multiple times)")
    print("   • Keep a backup of db.sqlite3 until you verify PostgreSQL is working")
    print()

if __name__ == "__main__":
    generate_postgres_seed()

