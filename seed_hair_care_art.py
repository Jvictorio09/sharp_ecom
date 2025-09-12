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
    "hero": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698759/3_phbtxn.jpg",  # shampoo
    "accent": "https://res.cloudinary.com/dkjtfjnlf/image/upload/v1756698753/302b99a5-5723-4846-b55b-aee584f54c50_jsty69.jpg",  # conditioner
}

def run(overwrite=False):
    title = "The Art of Modern Hair Care: Beyond Shampoo & Conditioner"
    slug = "art-of-hair-care"

    if overwrite:
        Post.objects.filter(slug=slug).delete()

    post, created = Post.objects.get_or_create(
        slug=slug,
        defaults=dict(
            title=title,
            excerpt="Hair care today is more than washing and conditioning — it’s a ritual of self-expression, balance, and modern science meeting timeless nature.",
            published_at=timezone.now(),
            author_name="SHARP Editorial",
            cover_image_url=IMAGES["hero"],
        ),
    )

    # Reset blocks
    PostBlock.objects.filter(post=post).delete()
    order = 0
    def add(kind, **kwargs):
        nonlocal order
        order += 1
        PostBlock.objects.create(post=post, order=order, kind=kind, **kwargs)

    # Lead
    add("paragraph", text=dedent("""
        Healthy, radiant hair has never been about following trends — it’s about understanding the art behind the care.
        The modern routine is no longer just shampoo and conditioner. It’s a thoughtful ritual where hydration, balance,
        and nourishment come together to express your identity with quiet confidence.
    """).strip())

    # Section 1
    add("heading", level="h2", text="Why Rituals Matter More Than Routines")
    add("paragraph", text=dedent("""
        A routine is a task you repeat. A ritual is an act of intention.
        When it comes to hair care, that intention transforms the ordinary into the extraordinary.
        It’s the difference between rushing through a wash and savoring a moment that sets the tone for your entire day.
    """).strip())

    # Insert 1 strong image
    add("image", caption="SHARP Hair Care Ritual", image1_url=IMAGES["accent"])

    # Section 2
    add("heading", level="h2", text="Nature Meets Modern Science")
    add("paragraph", text=dedent("""
        Today’s best formulas don’t force you to choose between natural purity and scientific results.
        Botanicals like aloe, rosemary, and argan oil deliver softness and shine, while advanced proteins and vitamins
        strengthen from within. The synergy is where the magic happens.
    """).strip())

    # Section 3
    add("heading", level="h2", text="Minimal Products, Maximum Impact")
    add("paragraph", text=dedent("""
        Luxury isn’t about a crowded shelf — it’s about choosing fewer, smarter products that actually work.
        A hydrating conditioner that doubles as a leave-in. An oil blend that replaces three separate serums.
        This is the essence of quiet luxury: intentional simplicity with amplified results.
    """).strip())

    # Callout
    add("callout", text=dedent("""
        Remember: Your hair is not just something you style — it’s something you tell your story with.
        Care for it like you would any art form.
    """).strip())

    # CTA
    add("paragraph", text="✨ Explore SHARP’s natural collection and turn your routine into an art form → /products/")

    print(f"[seed] Blog seeded. Visit: /blog/{slug}/")

if __name__ == "__main__":
    overwrite = "--overwrite" in sys.argv
    run(overwrite=overwrite)
