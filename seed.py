import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
django.setup()

from myApp.models import Product, ProductComponent

def first_image(p: Product) -> str | None:
    g = getattr(p, "gallery", None) or []
    return (g[0] if g else None) or (p.image_url or None)

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

# Base SKUs (names should match what you seeded earlier)
sku = {
    "shampoo": Product.objects.get(name="Sharp Shampoo"),
    "conditioner": Product.objects.get(name="Sharp Conditioner"),
    "salt": Product.objects.get(name="Sharp Sea Salt Spray"),
    "oil": Product.objects.get(name="Sharp Treatment Oil"),
}

# Bundles with **exact JD prices** from your list
bundles = [
    {
        "name": "Full Package",
        "short": "Shampoo + Conditioner + Sea Salt + Oil",
        "desc": "Our best-value set for clean, hydrated, textured hair with polished finish. Free delivery.",
        "price": 60,   # JD
        "components": {sku["shampoo"]:1, sku["conditioner"]:1, sku["salt"]:1, sku["oil"]:1},
    },
    {
        "name": "Shampoo + Conditioner Duo",
        "short": "Daily clean + weightless moisture",
        "desc": "The everyday core routine. Gentle cleanse, smooth detangle, natural shine.",
        "price": 34,   # JD
        "components": {sku["shampoo"]:1, sku["conditioner"]:1},
    },
    {
        "name": "Shampoo + Oil Duo",
        "short": "Cleanse + polish",
        "desc": "Balanced wash meets frizz control for a sleek finish.",
        "price": 32,   # JD
        "components": {sku["shampoo"]:1, sku["oil"]:1},
    },
    {
        "name": "Conditioner + Oil Duo",
        "short": "Hydrate + polish",
        "desc": "Weightless moisture with flyaway-taming control.",
        "price": 32,   # JD
        "components": {sku["conditioner"]:1, sku["oil"]:1},
    },
    {
        "name": "Shampoo + Sea Salt Duo",
        "short": "Cleanse + texture",
        "desc": "Soft, healthy hair with natural volume and touchable grip.",
        "price": 30,   # JD
        "components": {sku["shampoo"]:1, sku["salt"]:1},
    },
    {
        "name": "Conditioner + Sea Salt Duo",
        "short": "Hydrate + texture",
        "desc": "Smooth detangle with beachy volume.",
        "price": 30,   # JD
        "components": {sku["conditioner"]:1, sku["salt"]:1},
    },
    {
        "name": "Sea Salt + Oil Duo",
        "short": "Texture + polish",
        "desc": "Matte grip with a glossy, controlled finish.",
        "price": 29,   # JD
        "components": {sku["salt"]:1, sku["oil"]:1},
    },
    {
        "name": "Shampoo + Conditioner + Oil Trio",
        "short": "Cleanse, hydrate, finish",
        "desc": "Balanced wash, smooth detangle, frizz control—your everyday glow-up.",
        "price": 50,   # JD
        "components": {sku["shampoo"]:1, sku["conditioner"]:1, sku["oil"]:1},
    },
]

for b in bundles:
    comp_imgs = [first_image(p) for p in b["components"].keys()]
    gallery_csv = csv_join(comp_imgs)
    defaults = {
        "short_description": b["short"],
        "description": b["desc"],
        "price": b["price"],  # stored as DecimalField
        "image_url": comp_imgs[0] if comp_imgs else "",
        "gallery_csv": gallery_csv,
        "is_active": True,
    }

    bundle, created = Product.objects.get_or_create(name=b["name"], defaults=defaults)
    if not created:
        for k, v in defaults.items():
            setattr(bundle, k, v)
    set_if_hasattr(bundle, is_bundle=True, free_delivery=True)
    bundle.save()

    ProductComponent.objects.filter(parent=bundle).delete()
    ProductComponent.objects.bulk_create([
        ProductComponent(parent=bundle, component=prod, quantity=qty)
        for prod, qty in b["components"].items()
    ])

    print(f"{'Added' if created else 'Updated'}: {bundle.name} — {bundle.price} JD")

print("Done.")
