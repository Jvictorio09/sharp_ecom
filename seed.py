import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
django.setup()

from myApp.models import Product

products = [
    {
        "name": "Shampoo",
        "short_description": "Cleans without stripping.",
        "description": "Balanced daily shampoo that removes buildup without drying out your hair.",
        "price": 399.00,
        "image_url": "https://images.unsplash.com/photo-1585237018402-6a4b58d8d07c?w=800&q=80",
    },
    {
        "name": "Conditioner",
        "short_description": "Moisture, slip, shine.",
        "description": "Weightless hydration for smooth detangling and lasting shine.",
        "price": 449.00,
        "image_url": "https://images.unsplash.com/photo-1585238341986-4be02e9f0f2b?w=800&q=80",
    },
    {
        "name": "Treatment Oil",
        "short_description": "Polish and frizz control.",
        "description": "Finishing oil that tames flyaways and adds instant polish.",
        "price": 599.00,
        "image_url": "https://images.unsplash.com/photo-1542452255191-c85a98f2c5b9?w=800&q=80",
    },
    {
        "name": "Sea Salt Spray",
        "short_description": "Texture and control.",
        "description": "Beach-inspired spray for volume, grip, and natural matte finish.",
        "price": 499.00,
        "image_url": "https://images.unsplash.com/photo-1582092728060-3b1dc7a9c2b3?w=800&q=80",
    },
]

for p in products:
    obj, created = Product.objects.get_or_create(name=p["name"], defaults=p)
    if created:
        print(f"Added {p['name']}")
    else:
        print(f"{p['name']} already exists")
