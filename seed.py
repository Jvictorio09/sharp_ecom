import os, django, re
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
django.setup()

from myApp.models import Product, ProductComponent
from decimal import Decimal

# --- CONFIG: choose what to update ---
UPDATE_FRONT_ONLY = True   # True = update image_url only; False = also update gallery_csv
# ------------------------------------

def first_image(p):
    g = getattr(p, "gallery", None) or []
    return (g[0] if g else None) or (getattr(p, "image_url", None) or None)

def csv_join(urls):
    out, seen = [], set()
    for u in urls:
        if u and u not in seen:
            out.append(u); seen.add(u)
    return ",".join(out)

def set_if_hasattr(obj, **fields):
    for k, v in fields.items():
        if hasattr(obj, k):
            setattr(obj, k, v)

def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.strip().lower())

# Base SKUs (names should match what you seeded earlier)
sku = {
    "shampoo": Product.objects.get(name="Sharp Shampoo"),
    "conditioner": Product.objects.get(name="Sharp Conditioner"),
    "salt": Product.objects.get(name="Sharp Sea Salt Spray"),
    "oil": Product.objects.get(name="Sharp Treatment Oil"),
}

# Bundle images (front). Keys are matched case/spacing-insensitively.
bundle_images = {
    norm("Shampoo + Oil Duo"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986070/Shampoo-_-Oil-Duo_lxqkql.jpg",
    norm("Shampoo + Conditioner + Sea Salt Trio"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986070/Shampoo-_-Conditioner-_-Sea-Salt-Trio_ivpk7b.jpg",
    norm("Shampoo + Conditioner Duo"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986070/Shampoo-_-Conditioner-Duo_jcl7u4.jpg",
    norm("Full Package"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Full-Package_jwpfyg.jpg",
    norm("Shampoo + Conditioner + Oil Trio"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Shampoo-_-Conditioner-_-Oil-Trio_adoupx.jpg",
    norm("Shampoo + Sea Salt Duo"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Shampoo-_-Sea-Salt-Duo_bchivy.jpg",
    norm("Sea Salt + Oil Duo"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Sea-Salt-_-Oil-Duo_vpjvpg.jpg",
    norm("Conditioner + Sea Salt Duo"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Conditioner-_-Sea-Salt-Duo_kzhyaj.jpg",
    norm("Conditioner + Oil Duo"):
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756986069/Conditioner-_-Oil-Duo_leowiu.jpg",
}

# Bundles with exact JD prices
bundles = [
    {
        "name": "Full Package",
        "short": "Shampoo + Conditioner + Sea Salt + Oil",
        "desc": "Our best-value set for clean, hydrated, textured hair with polished finish. Free delivery.",
        "price": Decimal("60"),
        "components": {sku["shampoo"]:1, sku["conditioner"]:1, sku["salt"]:1, sku["oil"]:1},
    },
    {
        "name": "Shampoo + Conditioner Duo",
        "short": "Daily clean + weightless moisture",
        "desc": "The everyday core routine. Gentle cleanse, smooth detangle, natural shine.",
        "price": Decimal("34"),
        "components": {sku["shampoo"]:1, sku["conditioner"]:1},
    },
    {
        "name": "Shampoo + Oil Duo",
        "short": "Cleanse + polish",
        "desc": "Balanced wash meets frizz control for a sleek finish.",
        "price": Decimal("32"),
        "components": {sku["shampoo"]:1, sku["oil"]:1},
    },
    {
        "name": "Conditioner + Oil Duo",
        "short": "Hydrate + polish",
        "desc": "Weightless moisture with flyaway-taming control.",
        "price": Decimal("32"),
        "components": {sku["conditioner"]:1, sku["oil"]:1},
    },
    {
        "name": "Shampoo + Sea Salt Duo",
        "short": "Cleanse + texture",
        "desc": "Soft, healthy hair with natural volume and touchable grip.",
        "price": Decimal("30"),
        "components": {sku["shampoo"]:1, sku["salt"]:1},
    },
    {
        "name": "Conditioner + Sea Salt Duo",
        "short": "Hydrate + texture",
        "desc": "Smooth detangle with beachy volume.",
        "price": Decimal("30"),
        "components": {sku["conditioner"]:1, sku["salt"]:1},
    },
    {
        "name": "Sea Salt + Oil Duo",
        "short": "Texture + polish",
        "desc": "Matte grip with a glossy, controlled finish.",
        "price": Decimal("29"),
        "components": {sku["salt"]:1, sku["oil"]:1},
    },
    {
        "name": "Shampoo + Conditioner + Oil Trio",
        "short": "Cleanse, hydrate, finish",
        "desc": "Balanced wash, smooth detangle, frizz control—your everyday glow-up.",
        "price": Decimal("50"),
        "components": {sku["shampoo"]:1, sku["conditioner"]:1, sku["oil"]:1},
    },
]

for b in bundles:
    comp_imgs = [first_image(p) for p in b["components"].keys()]
    fallback_front = comp_imgs[0] if comp_imgs else ""
    mapped_front = bundle_images.get(norm(b["name"]), None)
    front_image = mapped_front or fallback_front

    # Build defaults; selectively touch gallery based on switch
    defaults = {
        "short_description": b["short"],
        "description": b["desc"],
        "price": b["price"],  # DecimalField-safe
        "image_url": front_image or "",   # always update front image
        "is_active": True,
    }
    if not UPDATE_FRONT_ONLY:
        gallery_csv = csv_join(([front_image] if front_image else []) + comp_imgs)
        defaults["gallery_csv"] = gallery_csv

    bundle, created = Product.objects.get_or_create(name=b["name"], defaults=defaults)
    if not created:
        # Always refresh front image + text fields
        for k in ("short_description", "description", "price", "image_url", "is_active"):
            setattr(bundle, k, defaults[k])
        # Conditionally refresh gallery
        if not UPDATE_FRONT_ONLY and "gallery_csv" in defaults:
            setattr(bundle, "gallery_csv", defaults["gallery_csv"])

    set_if_hasattr(bundle, is_bundle=True, free_delivery=True)
    bundle.save()

    # Recreate components
    ProductComponent.objects.filter(parent=bundle).delete()
    ProductComponent.objects.bulk_create([
        ProductComponent(parent=bundle, component=prod, quantity=qty)
        for prod, qty in b["components"].items()
    ])

    mode = "front image" if UPDATE_FRONT_ONLY else "front+gallery"
    print(f"{'Added' if created else 'Updated'}: {bundle.name} — {bundle.price} JD — set {mode} -> {front_image or 'fallback'}")

print("Done.")
