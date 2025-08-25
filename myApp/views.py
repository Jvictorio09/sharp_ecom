from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.utils.html import escape

from .models import Product

# -----------------------
# Session Cart Helpers
# -----------------------
CART_KEY = "cart"  # session key


def _get_cart(session):
    """Get or init the cart dict from session."""
    cart = session.get(CART_KEY)
    if cart is None:
        cart = {}
        session[CART_KEY] = cart
    return cart


def _items_and_subtotal(cart_dict):
    """Build item rows + subtotal for templates."""
    items = []
    subtotal = Decimal("0.00")
    for pid_str, qty in cart_dict.items():
        product = Product.objects.filter(id=int(pid_str), is_active=True).first()
        if not product:
            continue
        qty = int(qty)
        line_total = product.price * qty
        subtotal += line_total
        items.append({"product": product, "qty": qty, "line_total": line_total})
    return items, subtotal


def _cart_json(session):
    """Serialize the cart to JSON for AJAX drawer."""
    cart = session.get(CART_KEY, {}) or {}
    items = []
    subtotal = Decimal("0.00")
    for pid, qty in cart.items():
        p = Product.objects.filter(id=int(pid), is_active=True).first()
        if not p:
            continue
        qty = int(qty)
        line_total = p.price * qty
        subtotal += line_total
        items.append({
            "id": p.id,
            "name": p.name,
            "image_url": p.image_url,
            "qty": qty,
            "line_total": f"{line_total:.2f}",
            "price": f"{p.price:.2f}",
            "slug": p.slug,
        })
    return {
        "count": sum(i["qty"] for i in items),
        "subtotal": f"{subtotal:.2f}",
        "items": items,
    }


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

# -----------------------
# Pages
# -----------------------

def home(request):
    featured = Product.objects.filter(is_active=True)[:4]
    return render(request, "home.html", {"featured": featured})


def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "products.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(is_active=True).exclude(id=product.id)[:4]
    return render(request, "product_detail.html", {"product": product, "related": related})


def cart_view(request):
    """Full-page cart view (GET fallback)."""
    cart = request.session.get(CART_KEY, {})
    items, subtotal = _items_and_subtotal(cart)
    return render(request, "cart.html", {"items": items, "subtotal": subtotal})


@require_POST
def cart_add(request, product_id):
    """Add item to cart via POST (supports AJAX)."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    qty = int(request.POST.get("qty", 1))
    qty = max(1, qty)

    cart = _get_cart(request.session)
    cart[str(product.id)] = cart.get(str(product.id), 0) + qty
    request.session.modified = True

    if _is_ajax(request):
        data = _cart_json(request.session)
        return JsonResponse({"ok": True, "cart": data, "message": f"Added {escape(product.name)} x{qty}"})

    messages.success(request, f"Added {product.name} (x{qty}) to cart.")
    return redirect("cart")


def cart_remove(request, product_id):
    """Remove item from cart (supports AJAX)."""
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    request.session.modified = True

    if _is_ajax(request):
        data = _cart_json(request.session)
        return JsonResponse({"ok": True, "cart": data})

    messages.info(request, "Item removed from cart.")
    return redirect("cart")


def cart_summary_json(request):
    """Return JSON summary for drawer refresh."""
    return JsonResponse({"ok": True, "cart": _cart_json(request.session)})


def checkout(request):
    """Checkout (Cash on Delivery stub)."""
    cart = _get_cart(request.session)
    items, subtotal = _items_and_subtotal(cart)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        email = request.POST.get("email", "").strip()
        notes = request.POST.get("notes", "").strip()

        if not items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")
        if not (full_name and phone and address):
            messages.error(request, "Please fill in Name, Phone, and Address.")
            return render(request, "checkout.html", {"items": items, "subtotal": subtotal})

        # TODO: save an Order model later
        request.session[CART_KEY] = {}
        request.session.modified = True
        messages.success(request, "Order placed! We’ll confirm via Email.")
        return redirect("thanks")

    return render(request, "checkout.html", {"items": items, "subtotal": subtotal})


def thanks(request):
    return render(request, "thanks.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        if not (name and message):
            messages.error(request, "Please provide your name and message.")
        else:
            # TODO: Save ContactMessage model later
            messages.success(request, "Thanks for reaching out — we’ll get back to you shortly.")
            return redirect("thanks")
    return render(request, "contact.html")
