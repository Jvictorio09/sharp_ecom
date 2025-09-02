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

# --- Source of truth for single products ---
SINGLES = [
    {
        "name": "Sharp Sea Salt Spray",
        "price": Decimal("15"),
        "short_description": "Dead Sea minerals for volume + touchable, long-lasting texture.",
        "description": (
            "🧪 SHARP Sea Salt Spray\n\n"
            "Formulated with natural Dead Sea minerals, this spray enhances hair strength, adds volume, "
            "and creates a long-lasting textured look. The mineral-rich composition helps balance the scalp "
            "and improves the hair’s natural structure for a healthier, defined finish."
        ),
    },
    {
        "name": "Sharp Shampoo",
        "price": Decimal("19"),
        "short_description": "Aloe + Argan + Rosemary; sulfate/silicone-free cleanse with shine.",
        "description": (
            "🧪 SHARP Shampoo\n\n"
            "Powered by Aloe Vera, Argan Oil, and Rosemary Oil, and fortified with Vitamins E & B5 plus silk protein, "
            "this shampoo nourishes the scalp, strengthens hair fibers, and improves elasticity and shine. "
            "Free from sulfates and silicones, it protects hair integrity for long-term health."
        ),
    },
    {
        "name": "Sharp Conditioner",
        "price": Decimal("19"),
        "short_description": "Coconut + Rice Oil for deep hydration, smooth detangle, zero heaviness.",
        "description": (
            "🧪 SHARP Conditioner\n\n"
            "Infused with Coconut Oil and Rice Oil, this conditioner provides deep hydration while reinforcing the "
            "cuticle structure. It reduces breakage, restores smoothness, and leaves the hair soft, shiny, and "
            "manageable — without unwanted heaviness."
        ),
    },
    {
        "name": "Sharp Treatment Oil",
        "price": Decimal("17"),
        "short_description": "Argan + Rosemary + Jojoba; repairs, seals ends, boosts scalp circulation.",
        "description": (
            "🧪 SHARP Oil Treatment\n\n"
            "A natural blend of Argan Oil, Rosemary Oil, and Jojoba Oil, this intensive treatment repairs damaged hair, "
            "seals split ends, and improves scalp circulation to stimulate stronger, healthier growth. It restores "
            "natural shine and resilience from root to tip."
        ),
    },
]

updated, missing = [], []

for data in SINGLES:
    try:
        p = Product.objects.get(name=data["name"])
    except Product.DoesNotExist:
        missing.append(data["name"])
        continue

    set_if_hasattr(
        p,
        price=data["price"],
        short_description=data["short_description"],
        description=data["description"],
        is_active=True,
        is_bundle=False,
    )

    # Only set image_url if it's completely empty and the model has it
    if hasattr(p, "image_url") and (not p.image_url):
        # no-op; keep empty or you can assign a fallback here if you want
        pass

    # Leave gallery_csv as-is so we don't clobber existing galleries
    p.save()
    updated.append(f"{p.name} — {p.price} JD")

# --- Console summary ---
print("Updated singles:")
for line in updated:
    print(" •", line)

if missing:
    print("\n⚠️ Not found (check exact names or seed first):")
    for n in missing:
        print(" •", n)

print("\nDone.")
