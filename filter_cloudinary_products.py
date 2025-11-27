#!/usr/bin/env python
"""
Filter seed_postgres.py to only keep products with Cloudinary images.
Simple script that reads, filters, and updates the seed file.
"""

import re
import json
from pathlib import Path

def has_cloudinary(url):
    """Check if URL contains Cloudinary."""
    return url and 'res.cloudinary.com' in str(url)

def main():
    seed_file = Path('seed_postgres.py')
    
    if not seed_file.exists():
        print(f"❌ Error: {seed_file} not found!")
        return
    
    print("=" * 70)
    print("Filtering seed_postgres.py for Cloudinary products only")
    print("=" * 70)
    print()
    
    # Read file
    print("📖 Reading seed file...")
    with open(seed_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_file = seed_file.with_suffix('.py.backup')
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Extract PRODUCTS_DATA - find the array boundaries
    print("🔍 Extracting and filtering products...")
    
    # Find where PRODUCTS_DATA = [ starts
    products_start_match = re.search(r'PRODUCTS_DATA\s*=\s*\[', content)
    if not products_start_match:
        print("❌ Could not find PRODUCTS_DATA")
        return
    
    # Find the matching closing bracket
    start_pos = products_start_match.end() - 1  # Include the [
    bracket_count = 0
    pos = start_pos
    in_string = False
    string_char = None
    escape = False
    
    while pos < len(content):
        char = content[pos]
        
        if escape:
            escape = False
            pos += 1
            continue
        
        if char == '\\':
            escape = True
            pos += 1
            continue
        
        if not in_string:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end_pos = pos + 1
                    break
            elif char in ('"', "'"):
                in_string = True
                string_char = char
        else:
            if char == string_char:
                in_string = False
                string_char = None
        
        pos += 1
    else:
        print("❌ Could not find end of PRODUCTS_DATA array")
        return
    
    products_str = content[start_pos:end_pos]
    
    try:
        import ast
        products_data = ast.literal_eval(products_str)
    except:
        try:
            products_data = json.loads(products_str)
        except Exception as e:
            print(f"❌ Could not parse products data: {e}")
            return
    
    print(f"   Found {len(products_data)} products")
    
    # Filter products
    cloudinary_products = []
    kept_names = set()
    
    for product in products_data:
        img_url = product.get('image_url', '') or ''
        gallery = product.get('gallery_csv', '') or ''
        
        if has_cloudinary(img_url) or has_cloudinary(gallery):
            cloudinary_products.append(product)
            kept_names.add(product['name'])
    
    print(f"   ✅ Keeping {len(cloudinary_products)} products with Cloudinary")
    print(f"   ❌ Removing {len(products_data) - len(cloudinary_products)} products")
    
    if not cloudinary_products:
        print("⚠️  No Cloudinary products found!")
        return
    
    # Show kept products
    print("\n📦 Products being kept:")
    for p in cloudinary_products[:10]:  # Show first 10
        print(f"   • {p['name']}")
    if len(cloudinary_products) > 10:
        print(f"   ... and {len(cloudinary_products) - 10} more")
    
    # Replace products data
    products_new = json.dumps(cloudinary_products, indent=4, ensure_ascii=False)
    content = content[:start_pos] + products_new + content[end_pos:]
    
    # Filter components - find array boundaries
    print("\n🔍 Filtering product components...")
    comp_start_match = re.search(r'PRODUCT_COMPONENTS_DATA\s*=\s*\[', content)
    if comp_start_match:
        comp_start = comp_start_match.end() - 1
        comp_bracket = 0
        comp_pos = comp_start
        comp_in_str = False
        comp_str_char = None
        comp_escape = False
        
        while comp_pos < len(content):
            char = content[comp_pos]
            if comp_escape:
                comp_escape = False
                comp_pos += 1
                continue
            if char == '\\':
                comp_escape = True
                comp_pos += 1
                continue
            if not comp_in_str:
                if char == '[':
                    comp_bracket += 1
                elif char == ']':
                    comp_bracket -= 1
                    if comp_bracket == 0:
                        comp_end = comp_pos + 1
                        break
                elif char in ('"', "'"):
                    comp_in_str = True
                    comp_str_char = char
            else:
                if char == comp_str_char:
                    comp_in_str = False
            comp_pos += 1
        else:
            comp_end = None
        
        if comp_end:
            try:
                import ast
                comp_data = ast.literal_eval(content[comp_start:comp_end])
                filtered_comp = [
                    c for c in comp_data
                    if c.get('parent_name') in kept_names and c.get('component_name') in kept_names
                ]
                comp_new = json.dumps(filtered_comp, indent=4, ensure_ascii=False)
                content = content[:comp_start] + comp_new + content[comp_end:]
                print(f"   ✅ Kept {len(filtered_comp)} components")
            except Exception as e:
                print(f"   ⚠️  Could not filter components: {e}")
    
    # Filter order items - find array boundaries
    print("🔍 Filtering order items...")
    oi_start_match = re.search(r'ORDER_ITEMS_DATA\s*=\s*\[', content)
    if oi_start_match:
        oi_start = oi_start_match.end() - 1
        oi_bracket = 0
        oi_pos = oi_start
        oi_in_str = False
        oi_str_char = None
        oi_escape = False
        
        while oi_pos < len(content):
            char = content[oi_pos]
            if oi_escape:
                oi_escape = False
                oi_pos += 1
                continue
            if char == '\\':
                oi_escape = True
                oi_pos += 1
                continue
            if not oi_in_str:
                if char == '[':
                    oi_bracket += 1
                elif char == ']':
                    oi_bracket -= 1
                    if oi_bracket == 0:
                        oi_end = oi_pos + 1
                        break
                elif char in ('"', "'"):
                    oi_in_str = True
                    oi_str_char = char
            else:
                if char == oi_str_char:
                    oi_in_str = False
            oi_pos += 1
        else:
            oi_end = None
        
        if oi_end:
            try:
                import ast
                oi_data = ast.literal_eval(content[oi_start:oi_end])
                filtered_oi = [oi for oi in oi_data if oi.get('product_name') in kept_names]
                oi_new = json.dumps(filtered_oi, indent=4, ensure_ascii=False)
                content = content[:oi_start] + oi_new + content[oi_end:]
                print(f"   ✅ Kept {len(filtered_oi)} order items")
            except Exception as e:
                print(f"   ⚠️  Could not filter order items: {e}")
    
    # Write updated file
    print("\n💾 Writing updated seed file...")
    with open(seed_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 70)
    print("✅ Filtering Complete!")
    print("=" * 70)
    print(f"   Products: {len(cloudinary_products)} kept, {len(products_data) - len(cloudinary_products)} removed")
    print(f"   Backup: {backup_file}")
    print()

if __name__ == "__main__":
    main()
