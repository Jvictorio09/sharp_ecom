#!/usr/bin/env python
"""
Automated script to extract all data from SQLite and create a seed file.
This will export all your products, orders, users, and other data into a reusable seed file.
"""

import os
import sys
import json
from datetime import datetime
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.core import serializers
from django.contrib.auth.models import User
from myApp.models import Product, Order, OrderItem, PromoCode, Post, PostBlock, Subscriber, FxRate, ProductComponent

def create_seed_file():
    """Create a comprehensive seed file from all database data."""
    
    print("Creating seed file from your SQLite database...")
    print("=" * 60)
    
    # Collect all data
    all_data = {}
    
    # 1. Export Users (admin accounts)
    print("Exporting Users...")
    try:
        users = User.objects.all()
        all_data['users'] = []
        for user in users:
            all_data['users'].append({
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
            })
        print(f"   Exported {len(all_data['users'])} users")
    except Exception as e:
        print(f"   Error exporting users: {e}")
        all_data['users'] = []
    
    # 2. Export Products
    print("📤 Exporting Products...")
    try:
        products = Product.objects.all()
        all_data['products'] = []
        for product in products:
            all_data['products'].append({
                'name': product.name,
                'sku': product.sku,
                'slug': product.slug,
                'short_description': product.short_description,
                'description': product.description,
                'price': float(product.price),
                'image_url': product.image_url,
                'is_active': product.is_active,
                'gallery_csv': product.gallery_csv,
                'is_bundle': product.is_bundle,
                'free_delivery': product.free_delivery,
                'created_at': product.created_at.isoformat(),
            })
        print(f"   ✅ Exported {len(all_data['products'])} products")
    except Exception as e:
        print(f"   ⚠️  Error exporting products: {e}")
        all_data['products'] = []
    
    # 3. Export Product Components (bundle relationships)
    print("📤 Exporting Product Components...")
    try:
        components = ProductComponent.objects.all()
        all_data['product_components'] = []
        for comp in components:
            all_data['product_components'].append({
                'parent_name': comp.parent.name,  # Use name instead of ID for portability
                'component_name': comp.component.name,
                'quantity': comp.quantity,
            })
        print(f"   ✅ Exported {len(all_data['product_components'])} product components")
    except Exception as e:
        print(f"   ⚠️  Error exporting product components: {e}")
        all_data['product_components'] = []
    
    # 4. Export Orders
    print("📤 Exporting Orders...")
    try:
        orders = Order.objects.all()
        all_data['orders'] = []
        for order in orders:
            all_data['orders'].append({
                'order_number': order.order_number,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat(),
                'cancel_reason': order.cancel_reason,
                'full_name': order.full_name,
                'phone': order.phone,
                'email': order.email,
                'address_line1': order.address_line1,
                'city': order.city,
                'province': order.province,
                'zip_code': order.zip_code,
                'country': order.country,
                'shipping_address': order.shipping_address,
                'shipping_address_text': order.shipping_address_text,
                'shipping_method': order.shipping_method,
                'payment_method': order.payment_method,
                'subtotal': float(order.subtotal),
                'shipping_cost': float(order.shipping_cost),
                'discount_total': float(order.discount_total),
                'grand_total': float(order.grand_total),
                'notes': order.notes,
                'status': order.status,
                'zoho_data': order.zoho_data,
            })
        print(f"   ✅ Exported {len(all_data['orders'])} orders")
    except Exception as e:
        print(f"   ⚠️  Error exporting orders: {e}")
        all_data['orders'] = []
    
    # 5. Export Order Items
    print("📤 Exporting Order Items...")
    try:
        order_items = OrderItem.objects.all()
        all_data['order_items'] = []
        for item in order_items:
            all_data['order_items'].append({
                'order_number': item.order.order_number,  # Use order_number instead of ID
                'product_name': item.product.name,        # Use product name instead of ID
                'name': item.name,
                'unit_price': float(item.unit_price),
                'quantity': item.quantity,
                'line_total': float(item.line_total),
                'cancel_reason': item.cancel_reason,
            })
        print(f"   ✅ Exported {len(all_data['order_items'])} order items")
    except Exception as e:
        print(f"   ⚠️  Error exporting order items: {e}")
        all_data['order_items'] = []
    
    # 6. Export Promo Codes
    print("📤 Exporting Promo Codes...")
    try:
        promos = PromoCode.objects.all()
        all_data['promo_codes'] = []
        for promo in promos:
            all_data['promo_codes'].append({
                'code': promo.code,
                'type': promo.type,
                'value': float(promo.value),
                'description': promo.description,
                'min_subtotal': float(promo.min_subtotal),
                'max_discount': float(promo.max_discount) if promo.max_discount else None,
                'countries_csv': promo.countries_csv,
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
        print(f"   ⚠️  Error exporting promo codes: {e}")
        all_data['promo_codes'] = []
    
    # 7. Export Posts (blog posts)
    print("📤 Exporting Blog Posts...")
    try:
        posts = Post.objects.all()
        all_data['posts'] = []
        for post in posts:
            all_data['posts'].append({
                'title': post.title,
                'slug': post.slug,
                'excerpt': post.excerpt,
                'cover_image': str(post.cover_image) if post.cover_image else None,
                'cover_image_url': post.cover_image_url,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'author_name': post.author_name,
            })
        print(f"   ✅ Exported {len(all_data['posts'])} blog posts")
    except Exception as e:
        print(f"   ⚠️  Error exporting posts: {e}")
        all_data['posts'] = []
    
    # 8. Export Post Blocks
    print("📤 Exporting Post Blocks...")
    try:
        blocks = PostBlock.objects.all()
        all_data['post_blocks'] = []
        for block in blocks:
            all_data['post_blocks'].append({
                'post_slug': block.post.slug,  # Use slug instead of ID
                'order': block.order,
                'kind': block.kind,
                'text': block.text,
                'level': block.level,
                'image1': str(block.image1) if block.image1 else None,
                'image2': str(block.image2) if block.image2 else None,
                'image1_url': block.image1_url,
                'image2_url': block.image2_url,
                'caption': block.caption,
                'prod_query': block.prod_query,
            })
        print(f"   ✅ Exported {len(all_data['post_blocks'])} post blocks")
    except Exception as e:
        print(f"   ⚠️  Error exporting post blocks: {e}")
        all_data['post_blocks'] = []
    
    # 9. Export Subscribers
    print("📤 Exporting Subscribers...")
    try:
        subscribers = Subscriber.objects.all()
        all_data['subscribers'] = []
        for sub in subscribers:
            all_data['subscribers'].append({
                'email': sub.email,
                'name': sub.name,
                'source': sub.source,
                'is_confirmed': sub.is_confirmed,
                'unsubscribed_at': sub.unsubscribed_at.isoformat() if sub.unsubscribed_at else None,
                'created_at': sub.created_at.isoformat(),
                'ip': str(sub.ip) if sub.ip else None,
                'ua': sub.ua,
                'confirm_token': sub.confirm_token,
            })
        print(f"   ✅ Exported {len(all_data['subscribers'])} subscribers")
    except Exception as e:
        print(f"   ⚠️  Error exporting subscribers: {e}")
        all_data['subscribers'] = []
    
    # 10. Export FX Rates
    print("📤 Exporting FX Rates...")
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
        print(f"   ⚠️  Error exporting FX rates: {e}")
        all_data['fx_rates'] = []
    
    # Create the seed file
    print("\n📝 Creating seed file...")
    
    seed_content = f'''#!/usr/bin/env python
"""
Auto-generated seed file from SQLite database.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total records: {sum(len(data) for data in all_data.values())}
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.contrib.auth.models import User
from myApp.models import Product, Order, OrderItem, PromoCode, Post, PostBlock, Subscriber, FxRate, ProductComponent

def seed_database():
    """Seed the database with all exported data."""
    print("🌱 Seeding database with exported data...")
    
    # Create users
    print("👤 Creating users...")
    for user_data in {all_data['users']}:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={{
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
                'is_active': user_data['is_active'],
                'date_joined': datetime.fromisoformat(user_data['date_joined']),
            }}
        )
        if created:
            user.set_password('admin123')  # Default password - change this!
            user.save()
            print(f"   ✅ Created user: {{user.username}}")
        else:
            print(f"   ℹ️  User already exists: {{user.username}}")
    
    # Create products
    print("📦 Creating products...")
    for product_data in {all_data['products']}:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults={{
                'sku': product_data['sku'],
                'slug': product_data['slug'],
                'short_description': product_data['short_description'],
                'description': product_data['description'],
                'price': Decimal(str(product_data['price'])),
                'image_url': product_data['image_url'],
                'is_active': product_data['is_active'],
                'gallery_csv': product_data['gallery_csv'],
                'is_bundle': product_data['is_bundle'],
                'free_delivery': product_data['free_delivery'],
                'created_at': datetime.fromisoformat(product_data['created_at']),
            }}
        )
        if created:
            print(f"   ✅ Created product: {{product.name}}")
        else:
            print(f"   ℹ️  Product already exists: {{product.name}}")
    
    # Create product components
    print("🔗 Creating product components...")
    for comp_data in {all_data['product_components']}:
        try:
            parent = Product.objects.get(name=comp_data['parent_name'])
            component = Product.objects.get(name=comp_data['component_name'])
            
            comp, created = ProductComponent.objects.get_or_create(
                parent=parent,
                component=component,
                defaults={{'quantity': comp_data['quantity']}}
            )
            if created:
                print(f"   ✅ Created component: {{parent.name}} → {{component.name}}")
            else:
                print(f"   ℹ️  Component already exists: {{parent.name}} → {{component.name}}")
        except Product.DoesNotExist:
            print(f"   ⚠️  Skipping component - parent or component not found: {{comp_data}}")
    
    # Create orders
    print("📋 Creating orders...")
    for order_data in {all_data['orders']}:
        order, created = Order.objects.get_or_create(
            order_number=order_data['order_number'],
            defaults={{
                'created_at': datetime.fromisoformat(order_data['created_at']),
                'updated_at': datetime.fromisoformat(order_data['updated_at']),
                'cancel_reason': order_data['cancel_reason'],
                'full_name': order_data['full_name'],
                'phone': order_data['phone'],
                'email': order_data['email'],
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
            }}
        )
        if created:
            print(f"   ✅ Created order: {{order.order_number}}")
        else:
            print(f"   ℹ️  Order already exists: {{order.order_number}}")
    
    # Create order items
    print("🛒 Creating order items...")
    for item_data in {all_data['order_items']}:
        try:
            order = Order.objects.get(order_number=item_data['order_number'])
            product = Product.objects.get(name=item_data['product_name'])
            
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
                print(f"   ✅ Created order item: {{item.name}}")
            else:
                print(f"   ℹ️  Order item already exists: {{item.name}}")
        except (Order.DoesNotExist, Product.DoesNotExist):
            print(f"   ⚠️  Skipping order item - order or product not found: {{item_data}}")
    
    # Create promo codes
    print("🎫 Creating promo codes...")
    for promo_data in {all_data['promo_codes']}:
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
                'created_at': datetime.fromisoformat(promo_data['created_at']),
                'updated_at': datetime.fromisoformat(promo_data['updated_at']),
            }}
        )
        if created:
            print(f"   ✅ Created promo code: {{promo.code}}")
        else:
            print(f"   ℹ️  Promo code already exists: {{promo.code}}")
    
    # Create posts
    print("📝 Creating blog posts...")
    for post_data in {all_data['posts']}:
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
        if created:
            print(f"   ✅ Created post: {{post.title}}")
        else:
            print(f"   ℹ️  Post already exists: {{post.title}}")
    
    # Create post blocks
    print("📄 Creating post blocks...")
    for block_data in {all_data['post_blocks']}:
        try:
            post = Post.objects.get(slug=block_data['post_slug'])
            
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
                print(f"   ✅ Created post block for: {{post.title}}")
            else:
                print(f"   ℹ️  Post block already exists for: {{post.title}}")
        except Post.DoesNotExist:
            print(f"   ⚠️  Skipping post block - post not found: {{block_data}}")
    
    # Create subscribers
    print("📧 Creating subscribers...")
    for sub_data in {all_data['subscribers']}:
        sub, created = Subscriber.objects.get_or_create(
            email=sub_data['email'],
            defaults={{
                'name': sub_data['name'],
                'source': sub_data['source'],
                'is_confirmed': sub_data['is_confirmed'],
                'unsubscribed_at': datetime.fromisoformat(sub_data['unsubscribed_at']) if sub_data['unsubscribed_at'] else None,
                'created_at': datetime.fromisoformat(sub_data['created_at']),
                'ip': sub_data['ip'],
                'ua': sub_data['ua'],
                'confirm_token': sub_data['confirm_token'],
            }}
        )
        if created:
            print(f"   ✅ Created subscriber: {{sub.email}}")
        else:
            print(f"   ℹ️  Subscriber already exists: {{sub.email}}")
    
    # Create FX rates
    print("💱 Creating FX rates...")
    for fx_data in {all_data['fx_rates']}:
        fx, created = FxRate.objects.get_or_create(
            base=fx_data['base'],
            quote=fx_data['quote'],
            defaults={{
                'rate': Decimal(str(fx_data['rate'])),
                'updated_at': datetime.fromisoformat(fx_data['updated_at']),
            }}
        )
        if created:
            print(f"   ✅ Created FX rate: {{fx.base}}/{{fx.quote}}")
        else:
            print(f"   ℹ️  FX rate already exists: {{fx.base}}/{{fx.quote}}")
    
    print("\\n🎉 Database seeding completed!")
    print("\\n📊 Summary:")
    print(f"   Users: {{User.objects.count()}}")
    print(f"   Products: {{Product.objects.count()}}")
    print(f"   Orders: {{Order.objects.count()}}")
    print(f"   Order Items: {{OrderItem.objects.count()}}")
    print(f"   Promo Codes: {{PromoCode.objects.count()}}")
    print(f"   Posts: {{Post.objects.count()}}")
    print(f"   Post Blocks: {{PostBlock.objects.count()}}")
    print(f"   Subscribers: {{Subscriber.objects.count()}}")
    print(f"   FX Rates: {{FxRate.objects.count()}}")

if __name__ == "__main__":
    seed_database()
'''
    
    # Write the seed file
    with open('seed_data.py', 'w', encoding='utf-8') as f:
        f.write(seed_content)
    
    print("✅ Seed file created: seed_data.py")
    
    # Also create a JSON backup
    with open('seed_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)
    
    print("✅ JSON backup created: seed_data.json")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EXPORT SUMMARY:")
    print(f"   Users: {len(all_data['users'])}")
    print(f"   Products: {len(all_data['products'])}")
    print(f"   Product Components: {len(all_data['product_components'])}")
    print(f"   Orders: {len(all_data['orders'])}")
    print(f"   Order Items: {len(all_data['order_items'])}")
    print(f"   Promo Codes: {len(all_data['promo_codes'])}")
    print(f"   Posts: {len(all_data['posts'])}")
    print(f"   Post Blocks: {len(all_data['post_blocks'])}")
    print(f"   Subscribers: {len(all_data['subscribers'])}")
    print(f"   FX Rates: {len(all_data['fx_rates'])}")
    print(f"   TOTAL RECORDS: {sum(len(data) for data in all_data.values())}")
    print("=" * 60)
    
    print("\n🎯 USAGE INSTRUCTIONS:")
    print("1. Copy seed_data.py to your production environment")
    print("2. Run: python seed_data.py")
    print("3. Or run: python manage.py shell -c 'exec(open(\"seed_data.py\").read()); seed_database()'")
    print("\n⚠️  IMPORTANT:")
    print("- Change the default password 'admin123' in the seed file")
    print("- Test the seed file in a development environment first")
    print("- The seed file is idempotent (safe to run multiple times)")

if __name__ == "__main__":
    create_seed_file()
