#!/usr/bin/env python
"""Pull complete inventory information from Zoho Inventory."""

import os
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.integrations.zoho_inventory import _get_access_token, _zget

def fetch_all_items():
    """Fetch all items from Zoho with pagination."""
    all_items = []
    page = 1
    per_page = 200  # Max allowed by Zoho
    
    while True:
        print(f"Fetching page {page}...", end=" ")
        result = _zget("items", params={"page": page, "per_page": per_page})
        
        items = result.get("items", [])
        all_items.extend(items)
        print(f"Got {len(items)} items")
        
        # Check if there are more pages
        page_context = result.get("page_context", {})
        has_more = page_context.get("has_more_page", False)
        
        if not has_more or not items:
            break
            
        page += 1
    
    return all_items

def main():
    print("=" * 80)
    print("ZOHO INVENTORY - COMPLETE STOCK INFORMATION")
    print("=" * 80)
    
    try:
        # Get access token
        print("\n📡 Connecting to Zoho Inventory...")
        _get_access_token()
        print("✅ Connected successfully!\n")
        
        # Fetch all items
        print("📦 Fetching all items...")
        items = fetch_all_items()
        
        print(f"\n✅ Total items found: {len(items)}\n")
        print("=" * 80)
        
        # Display in a formatted table
        header = f"{'NAME':<40} {'SKU':<25} {'STOCK':<10} {'REORDER':<10}"
        print(header)
        print("-" * 80)
        
        for item in items:
            name = (item.get('name') or 'N/A')[:39]
            sku = (item.get('sku') or 'N/A')[:24]
            stock = item.get('stock_on_hand', 0)
            reorder = item.get('reorder_level', 0)
            
            print(f"{name:<40} {sku:<25} {stock:<10} {reorder:<10}")
        
        print("=" * 80)
        
        # Summary statistics
        total_stock = sum(item.get('stock_on_hand', 0) for item in items)
        items_below_reorder = [
            item for item in items 
            if item.get('reorder_level', 0) > 0 and 
               item.get('stock_on_hand', 0) < item.get('reorder_level', 0)
        ]
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total items: {len(items)}")
        print(f"   Total stock on hand: {total_stock}")
        print(f"   Items below reorder level: {len(items_below_reorder)}")
        
        if items_below_reorder:
            print(f"\n⚠️  ITEMS BELOW REORDER LEVEL:")
            for item in items_below_reorder:
                name = item.get('name', 'N/A')
                stock = item.get('stock_on_hand', 0)
                reorder = item.get('reorder_level', 0)
                print(f"   - {name}: {stock} units (reorder at {reorder})")
        
        # Save to file
        output_file = "zoho_inventory_report.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ZOHO INVENTORY - COMPLETE STOCK INFORMATION\n")
            f.write("=" * 80 + "\n\n")
            f.write(header + "\n")
            f.write("-" * 80 + "\n")
            
            for item in items:
                name = (item.get('name') or 'N/A')[:39]
                sku = (item.get('sku') or 'N/A')[:24]
                stock = item.get('stock_on_hand', 0)
                reorder = item.get('reorder_level', 0)
                f.write(f"{name:<40} {sku:<25} {stock:<10} {reorder:<10}\n")
            
            f.write("=" * 80 + "\n\n")
            f.write(f"SUMMARY:\n")
            f.write(f"Total items: {len(items)}\n")
            f.write(f"Total stock on hand: {total_stock}\n")
            f.write(f"Items below reorder level: {len(items_below_reorder)}\n")
            
            if items_below_reorder:
                f.write(f"\nITEMS BELOW REORDER LEVEL:\n")
                for item in items_below_reorder:
                    name = item.get('name', 'N/A')
                    stock = item.get('stock_on_hand', 0)
                    reorder = item.get('reorder_level', 0)
                    f.write(f"- {name}: {stock} units (reorder at {reorder})\n")
        
        print(f"\n💾 Report saved to: {output_file}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

