# backfill_sku.py (place beside manage.py)

import os, django
from django.utils.text import slugify

# 1) Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")  # 👈 use your actual settings module
django.setup()

# 2) Safe to import models
from myApp.models import Product

def gen_sku(p):
    base = slugify(p.name).replace("-", "")[:12].upper() or "PROD"
    return f"SHARP-{base}-{p.id}"

def main():
    updated = 0
    for p in Product.objects.filter(sku__isnull=True).all():
        sku = gen_sku(p)
        p.sku = sku
        p.save(update_fields=["sku"])
        updated += 1
        print(f"Set SKU for {p.name}: {sku}")
    print(f"✅ Backfilled {updated} SKUs")

if __name__ == "__main__":
    main()
