#!/usr/bin/env python
"""
Filter seed_postgres.py to only include products with Cloudinary images
"""
import re

# Read the file
with open('seed_postgres.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find PRODUCTS_DATA section
match = re.search(r'(PRODUCTS_DATA = \[)(.*?)(\])', content, re.DOTALL)
if not match:
    print("Could not find PRODUCTS_DATA section")
    exit(1)

start_tag = match.group(1)
products_content = match.group(2)
end_tag = match.group(3)

# Parse products - find each product dictionary
products = []
current_product = ""
depth = 0
in_string = False
escape_next = False

for char in products_content:
    if escape_next:
        current_product += char
        escape_next = False
        continue
    
    if char == '\\':
        current_product += char
        escape_next = True
        continue
    
    if char == '"' and not escape_next:
        in_string = not in_string
        current_product += char
        continue
    
    if not in_string:
        if char == '{':
            depth += 1
            current_product += char
        elif char == '}':
            depth -= 1
            current_product += char
            if depth == 0:
                # Complete product found
                products.append(current_product.strip())
                current_product = ""
        else:
            current_product += char
    else:
        current_product += char

print(f"Found {len(products)} products")

# Filter products that have Cloudinary images
cloudinary_products = []
removed_count = 0

for product in products:
    # Check if image_url contains Cloudinary URL
    if 'res.cloudinary.com' in product:
        cloudinary_products.append(product)
    else:
        # Extract product name for logging
        name_match = re.search(r'"name":\s*"([^"]+)"', product)
        name = name_match.group(1) if name_match else "Unknown"
        print(f"Removing product: {name} (non-Cloudinary image)")
        removed_count += 1

print(f"\nKept {len(cloudinary_products)} products with Cloudinary images")
print(f"Removed {removed_count} products without Cloudinary images")

# Reconstruct the PRODUCTS_DATA section
new_products_content = ",\n".join(cloudinary_products)
new_products_section = start_tag + "\n" + new_products_content + "\n" + end_tag

# Replace in original content
new_content = content[:match.start()] + new_products_section + content[match.end():]

# Write back
with open('seed_postgres.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\nFile updated successfully!")

