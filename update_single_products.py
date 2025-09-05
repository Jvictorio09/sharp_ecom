# scripts/update_single_products.py
import os
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django
django.setup()

from myApp.models import Product

def set_if_hasattr(obj, **fields):
    for k, v in fields.items():
        if hasattr(obj, k):
            setattr(obj, k, v)

# --- Professional copy (consolidated) ----------------------------------------
DESC_SALT = (
    "Sea Salt Spray\n\n"
    "Create effortless beach waves with our mineral-rich sea salt spray that adds natural volume and texture.\n\n"
    "How to Use\n"
    "• Spray evenly on damp or dry hair.\n"
    "• Scrunch or style with fingers for natural texture.\n"
    "• Air-dry or diffuse for extra volume.\n\n"
    "What It Does\n"
    "• Adds natural volume and lift\n"
    "• Creates raw, beach-style texture\n"
    "• Helps balance scalp with essential minerals\n\n"
    "Key Ingredients\n"
    "• Dead Sea Minerals — strengthen hair fibers; support scalp balance\n"
    "• Magnesium & Calcium — support shine and elasticity\n"
)

DESC_SHAMPOO = (
    "Nourishing Shampoo\n\n"
    "Gently cleanse and strengthen your hair with our nutrient-rich formula.\n\n"
    "How to Use\n"
    "• Massage 2–3 pumps into wet hair and scalp.\n"
    "• Work into a rich lather and rinse well. Repeat if needed.\n\n"
    "What It Does\n"
    "• Cleanses without stripping natural oils\n"
    "• Strengthens roots and supports fiber repair\n"
    "• Boosts shine and elasticity\n\n"
    "Key Ingredients\n"
    "• Aloe Vera — hydrates and soothes scalp\n"
    "• Argan Oil — nourishes; protects against dryness\n"
    "• Rosemary Oil — stimulates scalp micro-circulation\n"
    "• Vitamins E & B5 — support resilient hair\n"
    "• Silk Protein — improves softness and shine\n"
)

DESC_CONDITIONER = (
    "Hydrating Conditioner\n\n"
    "Deeply hydrates and nourishes hair, smooths tangles, and improves softness and shine—without heaviness.\n\n"
    "How to Use\n"
    "• After shampooing, apply to mid-lengths and ends.\n"
    "• Leave for 2–3 minutes, then rinse well.\n\n"
    "What It Does\n"
    "• Deep hydration and softness\n"
    "• Helps repair split ends; strengthens strands\n"
    "• Improves smoothness, shine, and manageability\n\n"
    "Key Ingredients\n"
    "• Coconut Oil — restores moisture; adds softness\n"
    "• Rice Oil — strengthens; enhances flexibility\n"
    "• Vitamins E & B5 — support hydration and protection\n"
)

DESC_OIL = (
    "SHARP Natural Hair Treatment — Nourishing Oil Blend\n\n"
    "Repairs and nourishes damaged ends, reduces frizz, and adds healthy natural shine while supporting overall hair health.\n\n"
    "How to Use\n"
    "• Apply 2–4 drops to damp or dry hair, focusing on the ends.\n"
    "• Use daily as a leave-in, or overnight for deeper nourishment.\n\n"
    "Benefits\n"
    "• Repairs and nourishes split ends\n"
    "• Reduces frizz; boosts natural shine\n"
    "• Supports stronger, healthier hair\n\n"
    "Key Ingredients & Benefits\n"
    "• Sunflower Oil — moisturizes; protects from dryness\n"
    "• Sweet Almond Oil — adds nourishment and softness\n"
    "• Castor Oil — supports strength and growth\n"
    "• Coconut Oil — hydrates; enhances shine\n"
    "• Aloe Vera Extract — soothes scalp; hydrates hair\n"
    "• Laurel, Cress & Lavender Oils — nourish and revitalize\n"
    "• Garlic Oil — supports scalp health\n"
    "• Vitamin E (Tocopherol) — antioxidant protection; shine\n"
)

# --- Sources of truth for singles --------------------------------------------
SINGLES = [
    {
        "name": "Sharp Sea Salt Spray",
        "price": Decimal("15"),
        "short_description": "Mineral-rich sea salt for natural volume and textured hold.",
        "description": DESC_SALT,
        # images: only set if empty, we keep existing gallery for these
        "image_url": None,
        "gallery": [],
    },
    {
        "name": "Sharp Shampoo",
        "price": Decimal("19"),
        "short_description": "Aloe + Argan + Rosemary: gentle cleanse with strength and shine.",
        "description": DESC_SHAMPOO,
        "image_url": None,
        "gallery": [],
    },
    {
        "name": "Sharp Conditioner",
        "price": Decimal("19"),
        "short_description": "Coconut + Rice oils for deep hydration and smooth detangling.",
        "description": DESC_CONDITIONER,
        "image_url": None,
        "gallery": [],
    },
    {
        "name": "Sharp Treatment Oil",
        "price": Decimal("17"),
        "short_description": "Nourishing multi-oil blend: repairs ends, tames frizz, adds shine.",
        "description": DESC_OIL,
        # 👇 Force-update images for Treatment Oil
        "image_url": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092383/1_zc9pfx.jpg",
        "gallery": [
            "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092383/1_zc9pfx.jpg",
            "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092382/3_oofwzf.jpg",
            "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1757092382/2_faqvtp.jpg",
        ],
    },
]

updated, missing = [], []

for data in SINGLES:
    try:
        p = Product.objects.get(name=data["name"])
    except Product.DoesNotExist:
        missing.append(data["name"])
        continue

    # core fields
    set_if_hasattr(
        p,
        price=data["price"],
        short_description=data["short_description"],
        description=data["description"],
        is_active=True,
        is_bundle=False,
    )

    # images
    gallery = data.get("gallery") or []
    desired_image = data.get("image_url")

    # For Treatment Oil we want to force-update to new images.
    if data["name"] == "Sharp Treatment Oil":
        if hasattr(p, "image_url") and desired_image:
            p.image_url = desired_image
        if hasattr(p, "gallery_csv") and gallery:
            p.gallery_csv = ",".join(gallery)

    else:
        # For other items, only set a primary image if it's currently empty.
        if hasattr(p, "image_url") and (not getattr(p, "image_url", None)) and desired_image:
            p.image_url = desired_image
        # And only set gallery if currently empty.
        if hasattr(p, "gallery_csv") and (not getattr(p, "gallery_csv", "")) and gallery:
            p.gallery_csv = ",".join(gallery)

    p.save()
    updated.append(f"{p.name} — {p.price} JD")

# --- Console summary ----------------------------------------------------------
print("Updated singles:")
for line in updated:
    print(" •", line)

if missing:
    print("\n⚠️ Not found (check exact names or seed first):")
    for n in missing:
        print(" •", n)

print("\nDone.")
