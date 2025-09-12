import os, sys
from textwrap import dedent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django
django.setup()

from django.utils import timezone
from myApp.models import Post, PostBlock

IMAGES = {
    "conditioner": [
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/39fbf9e4-e3e0-488a-90cd-762f60351da7_elsobt.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698752/150ddba4-fcf1-4bd2-9443-b797e385de64_vr3tix.jpg",
    ],
    "seasalt": [
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-2_dzqwkx.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698755/05505087-3572-48c8-9338-dafbed984b41-3_ljrau1.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698756/05505087-3572-48c8-9338-dafbed984b41_zbwehv.jpg",
    ],
    "shampoo": [
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698760/5_dlyniy.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698758/2_ibkeof.jpg",
    ],
    "oil": [
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698762/2_maw4et.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698763/3_km7fmm.jpg",
        "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698761/1_wax9fy.jpg",
    ],
}

def run(overwrite=False):
    title = "Quiet Luxury for Your Hair: The SHARP Natural Hair Ritual"
    slug = "natural-hair-care"

    from myApp.models import Post, PostBlock
    if overwrite:
        Post.objects.filter(slug=slug).delete()

    post, created = Post.objects.get_or_create(
        slug=slug,
        defaults=dict(
            title=title,
            excerpt="Luxury is discipline. Discover the ritual of SHARP Natural Hair Care — where science meets botanicals, and every strand tells a story of strength, shine, and serenity.",
            published_at=timezone.now(),
            author_name="SHARP Editorial",
            cover_image_url=IMAGES["conditioner"][0],
        ),
    )

    # Clear blocks for idempotency
    PostBlock.objects.filter(post=post).delete()
    order = 0
    def add(kind, **kwargs):
        nonlocal order
        order += 1
        PostBlock.objects.create(post=post, order=order, kind=kind, **kwargs)

    # Lead (hook)
    add("paragraph", text=dedent("""
        Imagine stepping out the door each morning knowing your hair feels as effortless as it looks.
        That’s the promise of quiet luxury — not loud, not fleeting, but a ritual of care that whispers confidence.
        At SHARP, we’ve crafted a collection that doesn’t just style your hair — it transforms the way you experience it.
    """).strip())

    # Sea Salt Spray
    add("heading", level="h2", text="Sea Salt Spray — Raw Texture, Refined Confidence")
    add("paragraph", text=dedent("""
        Forget stiff sprays. Our mineral-rich Sea Salt Spray is your shortcut to undone, confident waves —
        texture that feels as natural as ocean air, with volume that lingers from sunrise to sunset.
    """).strip())
    for url in IMAGES["seasalt"]:
        add("image", caption="Sea Salt Spray", image1_url=url)

    # Shampoo
    add("heading", level="h2", text="Nourishing Shampoo — The Reset Button for Your Hair")
    add("paragraph", text=dedent("""
        This isn’t just shampoo. It’s a daily reset.
        A nutrient-rich formula that cleanses without compromise, stripping away the noise of buildup while
        protecting the harmony of your natural oils. Think of it as mindfulness in a bottle — clarity for your scalp, energy for your roots.
    """).strip())
    for url in IMAGES["shampoo"]:
        add("image", caption="Nourishing Shampoo", image1_url=url)

    # Conditioner
    add("heading", level="h2", text="Hydrating Conditioner — Gloss Without Weight")
    add("paragraph", text=dedent("""
        Too often, conditioners weigh hair down in the name of moisture. Not ours.
        The SHARP Hydrating Conditioner is feather-light, yet deeply reparative —
        restoring smoothness, sealing split ends, and leaving hair with that elusive, mirror-like shine that turns heads.
    """).strip())
    for url in IMAGES["conditioner"]:
        add("image", caption="Hydrating Conditioner", image1_url=url)

    # Oil
    add("heading", level="h2", text="Nourishing Oil Blend — Luxury in a Drop")
    add("paragraph", text=dedent("""
        Hair oil, elevated. Our blend doesn’t just coat strands — it revives them.
        A silky, nutrient-dense elixir that repairs damage, tames frizz, and infuses hair with a glassy glow.
        One to two drops is all it takes to step into your day with quiet, radiant confidence.
    """).strip())
    for url in IMAGES["oil"]:
        add("image", caption="Nourishing Oil Blend", image1_url=url)

    # CTA (hook to shop)
    add("callout", text=dedent("""
        Luxury isn’t more. Luxury is *enough*. Discover the SHARP ritual —
        a collection designed to simplify your shelf and amplify your shine.
    """).strip())
    add("paragraph", text="✨ Ready to begin your ritual? Explore the full SHARP Natural Hair Care collection → /products/")

    print(f"[seed] Blog seeded. Visit: /blog/{slug}/")

if __name__ == "__main__":
    overwrite = "--overwrite" in sys.argv
    run(overwrite=overwrite)
