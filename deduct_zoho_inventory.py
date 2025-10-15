#!/usr/bin/env python
"""Deduct 1 unit from all Zoho Inventory items (including composites)."""

import os
import sys
import time

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from myApp.integrations.zoho_inventory import _get_access_token, _zget, _zpost

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

def create_inventory_adjustment(item_id, item_name, item_sku, quantity_to_deduct=1):
    """
    Create an inventory adjustment to deduct quantity from an item.
    
    Uses Zoho's Inventory Adjustment API to reduce stock.
    """
    try:
        payload = {
            "date": time.strftime("%Y-%m-%d"),
            "reason": "Inventory deduction test - Manual adjustment",
            "description": f"Deducting {quantity_to_deduct} unit(s) from {item_name}",
            "line_items": [
                {
                    "item_id": item_id,
                    "quantity_adjusted": -quantity_to_deduct  # Negative for deduction
                }
            ]
        }
        
        result = _zpost("inventoryadjustments", payload)
        return result
    except Exception as e:
        raise Exception(f"Failed to adjust inventory for {item_name} ({item_sku}): {str(e)}")

def main():
    print("=" * 80)
    print("ZOHO INVENTORY - DEDUCT 1 UNIT FROM ALL ITEMS")
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
        
        # Filter items that have stock > 0
        items_with_stock = [
            item for item in items 
            if item.get('stock_on_hand', 0) > 0
        ]
        
        print(f"\n📊 Items with stock > 0: {len(items_with_stock)}")
        print(f"📊 Items with no stock: {len(items) - len(items_with_stock)}")
        print("=" * 80)
        
        if not items_with_stock:
            print("\n⚠️  No items with stock to deduct from!")
            return
        
        # Ask for confirmation
        print(f"\n⚠️  WARNING: This will deduct 1 unit from {len(items_with_stock)} items!")
        print("\nItems to be adjusted:")
        for item in items_with_stock[:10]:  # Show first 10
            name = item.get('name', 'N/A')
            sku = item.get('sku', 'N/A')
            stock = item.get('stock_on_hand', 0)
            item_type = item.get('item_type', 'N/A')
            print(f"  - {name} ({sku}): {stock} units [Type: {item_type}]")
        
        if len(items_with_stock) > 10:
            print(f"  ... and {len(items_with_stock) - 10} more items")
        
        print("\n" + "=" * 80)
        print("\n✅ Proceeding with inventory deduction...")
        # Auto-proceed without asking for confirmation
        # response = input("\n⚠️  Are you sure you want to proceed? (yes/no): ").strip().lower()
        # if response != 'yes':
        #     print("\n❌ Operation cancelled by user.")
        #     return
        
        print("\n" + "=" * 80)
        print("🚀 Starting inventory adjustments...")
        print("=" * 80 + "\n")
        
        # Process each item
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for idx, item in enumerate(items_with_stock, 1):
            item_id = item.get('item_id')
            item_name = item.get('name', 'Unknown')
            item_sku = item.get('sku', 'N/A')
            stock = item.get('stock_on_hand', 0)
            item_type = item.get('item_type', 'N/A')
            
            print(f"[{idx}/{len(items_with_stock)}] Processing: {item_name} ({item_sku})")
            print(f"    Type: {item_type}, Current Stock: {stock}")
            
            try:
                # Create inventory adjustment
                result = create_inventory_adjustment(item_id, item_name, item_sku, quantity_to_deduct=1)
                
                adjustment = result.get('inventoryadjustment', {})
                adjustment_number = adjustment.get('adjustment_number', 'N/A')
                
                print(f"    ✅ Success - Adjustment #{adjustment_number} created")
                success_count += 1
                
                # Rate limiting - be nice to the API
                time.sleep(0.5)  # 500ms delay between requests
                
            except Exception as e:
                print(f"    ❌ Failed: {str(e)}")
                failed_count += 1
                
                # Continue with next item even if one fails
                continue
        
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"✅ Successful adjustments: {success_count}")
        print(f"❌ Failed adjustments: {failed_count}")
        print(f"⏭️  Skipped (no stock): {len(items) - len(items_with_stock)}")
        print(f"📦 Total items processed: {len(items)}")
        print("=" * 80)
        
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} adjustments failed. Check the errors above.")
        else:
            print(f"\n🎉 All adjustments completed successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

