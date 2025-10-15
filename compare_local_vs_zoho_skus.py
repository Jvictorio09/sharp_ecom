#!/usr/bin/env python
"""Compare local database SKUs with Zoho SKUs."""

import os
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.models import Product
from myApp.integrations.zoho_inventory import _get_access_token, _zget

def main():
    print("=" * 80)
    print("SKU COMPARISON: Local Database vs Zoho Inventory")
    print("=" * 80)
    
    # Connect to Zoho
    print("\n📡 Connecting to Zoho...")
    _get_access_token()
    
    # Get local products
    print("📦 Fetching local products...")
    local_products = Product.objects.all().order_by('name')
    
    # Get Zoho items
    print("📦 Fetching Zoho items...")
    result = _zget("items", params={"per_page": 200})
    zoho_items = result.get("items", [])
    
    # Create SKU lookups
    zoho_skus = {item.get('sku'): item for item in zoho_items if item.get('sku')}
    
    print(f"\n📊 Found {len(local_products)} local products")
    print(f"📊 Found {len(zoho_items)} Zoho items")
    print("=" * 80)
    
    print("\nLOCAL PRODUCTS:")
    print("-" * 80)
    for product in local_products:
        sku = product.sku or "NO SKU"
        is_bundle = "🎁 BUNDLE" if product.is_bundle else "📦 Regular"
        in_zoho = "✅ In Zoho" if sku in zoho_skus else "❌ NOT in Zoho"
        
        print(f"{is_bundle} | {product.name}")
        print(f"           Local SKU: {sku}")
        
        if sku in zoho_skus:
            zoho_item = zoho_skus[sku]
            zoho_stock = zoho_item.get('stock_on_hand', 0)
            print(f"           Zoho Stock: {zoho_stock} units - {in_zoho}")
        else:
            print(f"           {in_zoho}")
        print()
    
    print("=" * 80)
    print("\nZOHO ITEMS (that don't match local):")
    print("-" * 80)
    
    local_skus = {p.sku for p in local_products if p.sku}
    unmatched_zoho = [item for item in zoho_items if item.get('sku') not in local_skus]
    
    for item in unmatched_zoho:
        name = item.get('name', 'N/A')
        sku = item.get('sku', 'N/A')
        stock = item.get('stock_on_hand', 0)
        print(f"📦 {name}")
        print(f"   SKU: {sku}")
        print(f"   Stock: {stock}")
        print()
    
    print("=" * 80)

if __name__ == "__main__":
    main()

