#!/usr/bin/env python
"""Check for composite items in Zoho Inventory and show their structure."""

import os
import sys
import json

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.integrations.zoho_inventory import _get_access_token, _zget

def fetch_all_items():
    """Fetch all items from Zoho with pagination."""
    all_items = []
    page = 1
    per_page = 200
    
    while True:
        print(f"Fetching page {page}...", end=" ")
        result = _zget("items", params={"page": page, "per_page": per_page})
        
        items = result.get("items", [])
        all_items.extend(items)
        print(f"Got {len(items)} items")
        
        page_context = result.get("page_context", {})
        has_more = page_context.get("has_more_page", False)
        
        if not has_more or not items:
            break
            
        page += 1
    
    return all_items

def get_item_details(item_id):
    """Fetch detailed information about a specific item."""
    try:
        result = _zget(f"items/{item_id}")
        return result.get("item", {})
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}")
        return {}

def main():
    print("=" * 80)
    print("ZOHO INVENTORY - COMPOSITE ITEMS CHECK")
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
        
        # Categorize items
        regular_items = []
        composite_items = []
        bundle_items = []
        
        for item in items:
            item_type = item.get('item_type', '')
            is_combo = item.get('is_combo_product', False)
            
            if item_type == 'composite':
                composite_items.append(item)
            elif is_combo:
                bundle_items.append(item)
            else:
                regular_items.append(item)
        
        print(f"\n📊 ITEM BREAKDOWN:")
        print(f"   Regular items: {len(regular_items)}")
        print(f"   Composite items: {len(composite_items)}")
        print(f"   Bundle/Combo items: {len(bundle_items)}")
        print("=" * 80)
        
        # Show composite items in detail
        if composite_items:
            print(f"\n🔍 COMPOSITE ITEMS FOUND ({len(composite_items)}):")
            print("=" * 80)
            
            for item in composite_items:
                name = item.get('name', 'N/A')
                sku = item.get('sku', 'N/A')
                item_id = item.get('item_id')
                stock = item.get('stock_on_hand', 0)
                
                print(f"\n📦 {name}")
                print(f"   SKU: {sku}")
                print(f"   Stock: {stock}")
                print(f"   Item ID: {item_id}")
                
                # Get detailed info
                details = get_item_details(item_id)
                mapped_items = details.get('mapped_items', [])
                
                if mapped_items:
                    print(f"   Components:")
                    for component in mapped_items:
                        comp_name = component.get('name', 'N/A')
                        comp_qty = component.get('quantity', 0)
                        comp_sku = component.get('sku', 'N/A')
                        print(f"     - {comp_qty}x {comp_name} ({comp_sku})")
                else:
                    print(f"   No components found")
                
        else:
            print(f"\n⚠️  No composite items found!")
            print("   All items are regular inventory items.")
        
        # Show bundle items
        if bundle_items:
            print(f"\n\n🔍 BUNDLE/COMBO ITEMS FOUND ({len(bundle_items)}):")
            print("=" * 80)
            
            for item in bundle_items:
                name = item.get('name', 'N/A')
                sku = item.get('sku', 'N/A')
                print(f"   - {name} ({sku})")
        
        # Check items that look like bundles but aren't marked as such
        potential_bundles = [
            item for item in regular_items
            if any(keyword in item.get('name', '').lower() 
                   for keyword in ['duo', 'trio', 'package', 'bundle', 'set', '+'])
        ]
        
        if potential_bundles:
            print(f"\n\n🔍 POTENTIAL BUNDLES (not marked as composite/combo):")
            print("=" * 80)
            
            for item in potential_bundles:
                name = item.get('name', 'N/A')
                sku = item.get('sku', 'N/A')
                stock = item.get('stock_on_hand', 0)
                item_type = item.get('item_type', 'N/A')
                
                print(f"\n📦 {name}")
                print(f"   SKU: {sku}")
                print(f"   Type: {item_type}")
                print(f"   Stock: {stock}")
                
                # Get full details
                item_id = item.get('item_id')
                details = get_item_details(item_id)
                
                # Check various fields that might indicate bundle structure
                has_mapped = bool(details.get('mapped_items'))
                has_composite = bool(details.get('composite_items'))
                is_composite = details.get('is_composite_item', False)
                
                print(f"   Has mapped_items: {has_mapped}")
                print(f"   Has composite_items: {has_composite}")
                print(f"   is_composite_item: {is_composite}")
                
                if has_mapped or has_composite:
                    print(f"   ⚠️  This item has component data!")
                    if has_mapped:
                        print(f"   Mapped items: {json.dumps(details.get('mapped_items'), indent=4)}")
                    if has_composite:
                        print(f"   Composite items: {json.dumps(details.get('composite_items'), indent=4)}")
        
        print("\n" + "=" * 80)
        print("✅ Check complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

