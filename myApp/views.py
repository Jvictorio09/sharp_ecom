# myApp/views.py
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST

from .models import Product, Order, OrderItem

# =======================
# Session Cart Helpers
# =======================
CART_KEY = "cart"  # session key

import re

def _normalize_order_number(raw: str) -> str:
    """
    Normalize inputs like ' sh 123456 ' or 'sh-123456' to 'SH-123456'.
    If it already looks like SH-xxxxxx, it returns the uppercase version.
    """
    s = (raw or "").strip().upper()
    s = re.sub(r"\s+", "", s)        # remove all spaces
    # If missing hyphen and matches SH\d{6}, insert hyphen after SH
    if re.fullmatch(r"SH\d{6}", s):
        return f"SH-{s[2:]}"
    return s


def _get_cart(session):
    """Get or init cart dict from session: {product_id: qty}."""
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
        qty = max(1, int(qty))
        line_total = (product.price * qty).quantize(Decimal("0.01"))
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
        qty = max(1, int(qty))
        line_total = (p.price * qty).quantize(Decimal("0.01"))
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


# =======================
# Pages
# =======================
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
    """Full-page cart view."""
    cart = request.session.get(CART_KEY, {})
    items, subtotal = _items_and_subtotal(cart)
    return render(request, "cart.html", {"items": items, "subtotal": subtotal})


@require_POST
def cart_add(request, product_id):
    """Add item to cart (supports AJAX)."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    qty = max(1, int(request.POST.get("qty", 1)))

    cart = _get_cart(request.session)
    cart[str(product.id)] = cart.get(str(product.id), 0) + qty
    request.session.modified = True

    if _is_ajax(request):
        data = _cart_json(request.session)
        return JsonResponse({"ok": True, "cart": data, "message": f"Added {escape(product.name)} x{qty}"})

    messages.success(request, f"Added {product.name} (x{qty}) to cart.")
    return redirect("cart")


@require_POST
def cart_update(request, product_id):
    """
    Update quantity for a cart line (supports AJAX).
    POST: qty (>=1) ; if qty <=0, removes the item.
    """
    qty = int(request.POST.get("qty", 1))
    cart = _get_cart(request.session)
    key = str(product_id)

    if qty <= 0:
        cart.pop(key, None)
    else:
        if Product.objects.filter(id=product_id, is_active=True).exists():
            cart[key] = qty
        else:
            cart.pop(key, None)

    request.session.modified = True

    if _is_ajax(request):
        return JsonResponse({"ok": True, "cart": _cart_json(request.session)})

    return redirect("cart")


@require_POST
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
    """
    Checkout — creates Order + OrderItems, sends emails, clears cart.
    Supports both the old address field name `address` and new `address_line1`.
    """
    cart = _get_cart(request.session)
    items, subtotal = _items_and_subtotal(cart)

    if request.method == "POST":
        # Contact
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()

        # Address (new preferred; fallback to `address`)
        address_line1 = request.POST.get("address_line1", "").strip() or request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        province = request.POST.get("province", "").strip()
        zip_code = request.POST.get("zip", "").strip()
        notes = request.POST.get("notes", "").strip()

        # Choices
        shipping_method = request.POST.get("shipping", "standard")
        payment_method = request.POST.get("payment", "cod")

        if not items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")
        if not (full_name and phone and address_line1):
            messages.error(request, "Please fill in Full Name, Phone, and Address.")
            return render(request, "checkout.html", {"items": items, "subtotal": subtotal})

        # Shipping cost
        shipping_cost = Decimal("0.00") if shipping_method == "standard" else Decimal("299.00")
        discount_total = Decimal("0.00")  # Add server-side promo calc later
        grand_total = (subtotal + shipping_cost - discount_total).quantize(Decimal("0.01"))

        # Create Order
        order = Order.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            address_line1=address_line1,
            city=city,
            province=province,
            zip_code=zip_code,
            notes=notes,
            shipping_method=shipping_method,
            payment_method=payment_method,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            discount_total=discount_total,
            grand_total=grand_total,
            status="pending",
        )

        # Items
        for row in items:
            p = row["product"]
            qty = row["qty"]
            line_total = (p.price * qty).quantize(Decimal("0.01"))
            OrderItem.objects.create(
                order=order,
                product=p,
                name=p.name,
                unit_price=p.price,
                quantity=qty,
                line_total=line_total,
            )

        # Clear cart
        request.session[CART_KEY] = {}
        request.session.modified = True

        # Emails
        _email_order_confirmation(request, order)
        _email_admin_new_order(request, order)

        messages.success(request, "Order placed! We’ve emailed your confirmation.")
        return redirect(f"/thanks/?o={order.order_number}")

    return render(request, "checkout.html", {"items": items, "subtotal": subtotal})


def thanks(request):
    order_number = request.GET.get("o", "")
    return render(request, "thanks.html", {"order_number": order_number})


# =======================
# Order Status / Detail
# =======================
def order_status(request):
    """
    Public lookup: order number + optional email.
    - If email is provided: must match (case-insensitive).
    - If email is blank: allow lookup by order number only.
    - Order number normalization: handles spaces, lowercase, and missing hyphen.
    """
    context = {}
    if request.method == "POST":
        raw_order_number = request.POST.get("order_number") or ""
        input_email = (request.POST.get("email") or "").strip().lower()

        order_number = _normalize_order_number(raw_order_number)

        # Try exact first
        order = Order.objects.filter(order_number=order_number).first()

        # If not found and user pasted something odd like 'SH - 123456', remove non-alnum and retry
        if not order:
            alt = re.sub(r"[^A-Z0-9]", "", order_number)   # keep only A-Z0-9
            # Rebuild as SH-xxxxxx if it matches
            if re.fullmatch(r"SH\d{6}", alt):
                order = Order.objects.filter(order_number=f"SH-{alt[2:]}").first()

        if not order:
            messages.error(request, "We couldn’t find an order with those details.")
        else:
            # Only enforce email check if the user actually entered one.
            if input_email:
                if order.email and order.email.strip().lower() != input_email:
                    messages.error(request, "We couldn’t find an order with those details.")
                else:
                    context["order"] = order
            else:
                # No email provided; allow lookup by order number alone.
                context["order"] = order

    return render(request, "order_status.html", context)


def order_detail(request, order_number):
    """Auth-less, read-only order detail by order number."""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "order_detail.html", {"order": order})


# =======================
# Contact
# =======================
# myApp/views.py
# myApp/views_contact.py  (or keep inside views.py if you prefer)

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def contact(request):
    """
    Contact page:
    - Sends an admin notification email.
    - Sends a branded HTML auto-reply to the user (if they provided a valid email).
    - Redirects to a dedicated 'contact_thanks' page on success.
    """
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        message = (request.POST.get("message") or "").strip()

        # Basic validation
        if not name or not message:
            messages.error(request, "Please provide your name and message.")
            return render(request, "contact.html", {"name": name, "email": email, "message_text": message})

        # Validate email if provided (optional field)
        user_email_ok = False
        if email:
            try:
                validate_email(email)
                user_email_ok = True
            except ValidationError:
                # We won't block the submit—just skip the auto-reply
                user_email_ok = False

        # --- Admin notification ---
        admin_to = getattr(settings, "CONTACT_TO", None) or getattr(settings, "DEFAULT_FROM_EMAIL", None)
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        if admin_to and from_email:
            subject = f"New contact from {name}"
            body = f"Name: {name}\nEmail: {email or 'N/A'}\n\nMessage:\n{message}"
            try:
                send_mail(subject, body, from_email, [admin_to], fail_silently=False)
            except Exception:
                # Don't crash UX on mail issues—log in real apps
                messages.warning(request, "Your message was received, but we couldn’t notify our team by email. We’ll still follow up.")

        # --- Auto-reply to sender (HTML + plain text fallback) ---
        if user_email_ok and from_email:
            try:
                context = {
                    "name": name,
                    "user_message": message,
                    "products_url": request.build_absolute_uri("/products/"),
                    "order_status_url": request.build_absolute_uri("/order-status/"),
                    "support_email": admin_to or from_email,
                }
                html = render_to_string("emails/contact_autoreply.html", context)
                text = strip_tags(html)  # simple plaintext fallback

                send_mail(
                    subject="Thanks for contacting SHARP — We’re on it",
                    message=text,
                    from_email=from_email,
                    recipient_list=[email],
                    html_message=html,
                    fail_silently=True,  # don't break UX if the auto-reply fails
                )
            except Exception:
                pass  # swallow auto-reply errors; optional: log

        messages.success(request, "Thanks for reaching out — your message has been received.")
        return redirect("contact_thanks")

    # GET
    return render(request, "contact.html")


def contact_thanks(request):
    """
    Simple thank-you page after contact submission.
    """
    return render(request, "contact_thanks.html")


# =======================
# Email helpers
# =======================
def _email_order_confirmation(request, order):
    if not order.email:
        return
    context = {
        "order": order,
        "items": list(order.items.all()),  # <-- add this
        "request": request,
    }
    subject = f"Your SHARP Order {order.order_number}"
    text_body = render_to_string("emails/order_confirmation.txt", context)
    html_body = render_to_string("emails/order_confirmation.html", context)
    send_mail(subject, text_body, settings.DEFAULT_FROM_EMAIL, [order.email], html_message=html_body)


def _email_admin_new_order(request, order: Order):
    """Notify admin of a new order."""
    admin_email = getattr(settings, "ADMIN_ORDER_EMAIL", None)
    if not admin_email:
        return

    try:
        items_qs = order.items.all()
    except Exception:
        items_qs = order.orderitem_set.all()

    context = {"order": order, "items": items_qs, "request": request}

    subject = f"New Order: {order.order_number}"
    text_body = render_to_string("emails/admin_new_order.txt", context)
    # If you later add HTML: html_body = render_to_string("emails/admin_new_order.html", context)

    send_mail(
        subject=subject,
        message=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[admin_email],
    )
