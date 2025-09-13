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
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Product, Order, OrderItem

# --- Email safety helper (never crash the request) ---
# --- Email safety helper (never crash the request) ---
import logging
from django.core.mail import get_connection, EmailMultiAlternatives

logger = logging.getLogger(__name__)

from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_GET

from .models import Order, OrderItem, PromoCode

# If you already have money_filter, we'll call it; else fall back.
def _money(val, request=None):
    try:
        # existing helper in your project
        return money_filter(val, request)  # type: ignore[name-defined]
    except Exception:
        try:
            return f"{Decimal(str(val or '0')):,.2f}"
        except Exception:
            return "0.00"

# --- Resend sender (HTTP) ---
import requests

def _send_email_resend(*, subject, text_body, to_list, html_body=None, reply_to=None, headers=None) -> bool:
    """
    Sends email using Resend HTTP API.
    Reads credentials from settings.RESEND (API_KEY, FROM, REPLY_TO, BASE_URL).
    Returns True/False.
    """
    try:
        cfg = getattr(settings, "RESEND", {}) or {}
        api_key = cfg.get("API_KEY")
        sender  = cfg.get("FROM") or getattr(settings, "DEFAULT_FROM_EMAIL", None)
        base    = cfg.get("BASE_URL", "https://api.resend.com")
        if not (api_key and sender and to_list):
            logger.error("Resend missing config or recipients. sender=%s to=%s", sender, to_list)
            return False

        payload = {
            "from": sender,
            "to": to_list,
            "subject": subject or "",
        }
        if html_body:
            payload["html"] = html_body
        if text_body:
            payload["text"] = text_body
        # Prefer explicit arg, else settings.RESEND.REPLY_TO
        payload["reply_to"] = reply_to or cfg.get("REPLY_TO")
        if headers:
            payload["headers"] = headers

        r = requests.post(
            f"{base.rstrip('/')}/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        if r.status_code != 200:
            logger.error("Resend error %s: %s", r.status_code, r.text[:500])
            return False
        return True
    except Exception as e:
        logger.exception("Resend send failed: %s", e)
        return False


# myApp/views.py
# === currency formatter bridge ==========================================
from importlib import import_module
from functools import lru_cache
from decimal import Decimal as _D

@lru_cache(maxsize=1)
def _get_money_callable():
    """
    Use the same callable your template filter uses.
    Tries 'money' then 'money_filter'. Cached after first lookup.
    """
    try:
        mod = import_module("myApp.templatetags.money")
        fn = getattr(mod, "money", None) or getattr(mod, "money_filter", None)
        return fn
    except Exception:
        return None

def money_filter(amount, request=None) -> str:
    """
    View-side formatter that mirrors {{ value|money:request }}.
    Falls back to plain number formatting if the tag isn’t importable.
    """
    fn = _get_money_callable()
    if fn:
        return fn(amount, request)
    try:
        return f"{_D(str(amount or '0')):,.2f}"
    except Exception:
        return "0.00"
# ========================================================================

# --- Email safety helper (never crash the request) ---
import logging
from django.core.mail import get_connection, EmailMultiAlternatives

logger = logging.getLogger(__name__)

def _safe_send_mail(subject, text_body, from_email, to_list, html_body=None, extra_headers=None):
    """
    Compatibility shim: route all mail through Resend.
    - Ignores from_email (Resend uses settings.RESEND['FROM'])
    - extra_headers may include 'Reply-To'; we map it to Resend's reply_to
    """
    reply_to = None
    if isinstance(extra_headers, dict):
        reply_to = extra_headers.get("Reply-To") or extra_headers.get("Reply_to") or extra_headers.get("reply-to")

    return _send_email_resend(
        subject=subject,
        text_body=text_body,
        to_list=to_list,
        html_body=html_body,
        reply_to=reply_to,
        headers=None,  # pass through custom headers if you really need them
    )




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



def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


# =======================
# Pages
# =======================
# myApp/views.py
from django.db.models import Prefetch
from .models import Product, Order, OrderItem, ProductComponent  # + ProductComponent

@ensure_csrf_cookie
def home(request):
    featured = (
        Product.objects
        .filter(is_active=True, is_bundle=False)
        .order_by('name')[:4]
    )

    bundle_links = Prefetch(
        'component_links',
        queryset=ProductComponent.objects.select_related('component')
    )
    bundles = (
        Product.objects
        .filter(is_active=True, is_bundle=True)
        .prefetch_related(bundle_links)
        .order_by('name')[:4]
    )

    return render(request, "home.html", {
        "featured": featured,
        "bundles": bundles,   # ← new
    })



# myApp/views.py
from django.db.models import Prefetch
from .models import Product, ProductComponent  # add ProductComponent

@ensure_csrf_cookie
def product_list(request):
    q_type = (request.GET.get("type") or "all").lower()

    qs = Product.objects.filter(is_active=True).order_by("name")
    if q_type == "bundle":
        qs = qs.filter(is_bundle=True)
    elif q_type == "single":
        qs = qs.filter(is_bundle=False)

    # Prefetch bundle components only if we’re showing any bundles
    if qs.filter(is_bundle=True).exists():
        qs = qs.prefetch_related(
            Prefetch("component_links", queryset=ProductComponent.objects.select_related("component"))
        )

    return render(request, "products.html", {"products": qs, "q_type": q_type})

@ensure_csrf_cookie
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

from decimal import Decimal

def _post_first(request, *names) -> str:
    """Return the first non-empty POST value among the given names."""
    for n in names:
        v = (request.POST.get(n) or "").strip()
        if v:
            return v
    return ""
# views.py
from decimal import Decimal
import re
import threading

from django.contrib import messages
from django.http import JsonResponse, Http404
from django.shortcuts import redirect, render
from django.db import transaction
from django.urls import reverse

from django_countries import countries

from .models import Order, OrderItem
# from .utils import _get_cart, _items_and_subtotal, _email_order_confirmation, _email_admin_new_order, CART_KEY
# ^ uncomment / adjust imports to match your project layout

# -----------------------------
# Shipping destinations
# -----------------------------
# Middle East (curated) + USA. Adjust as needed.
SHIP_TO = [
    "AE",  # United Arab Emirates
    "SA",  # Saudi Arabia
    "QA",  # Qatar
    "KW",  # Kuwait
    "OM",  # Oman
    "BH",  # Bahrain
    "JO",  # Jordan
    "LB",  # Lebanon
    "EG",  # Egypt
    "US",  # United States
]
SHIP_TO_COUNTRIES = [(code, dict(countries)[code]) for code in SHIP_TO]

# -----------------------------
# Address schemas (client + server mirror)
# -----------------------------
ADDRESS_RULES = {
    "PH": {
        "fields": [
            {"key": "address_line1", "label": "House/Unit, Street, Building", "required": True},
            {"key": "barangay", "label": "Barangay", "required": True},
            {"key": "city", "label": "City / Municipality", "required": True},
            {"key": "province", "label": "Province", "required": True},
            {"key": "postal_code", "label": "ZIP Code", "required": True, "pattern": r"^[0-9]{4}$"},
        ],
        "example": "406 Diamond Lane, Cristimar Village, Brgy. San Roque, Antipolo City",
    },
    "JO": {
        "fields": [
            {"key": "address_line1", "label": "Building / Street", "required": True},
            {"key": "area", "label": "Area", "required": True, "type": "select",
             "options": ["Amman","Zarqa","Irbid","Balqa","Mafraq","Madaba","Karak","Tafilah","Ma'an","Aqaba","Jerash","Ajloun","Other"]},
            {"key": "area_other", "label": "If Other, specify",
             "requiredIf": {"field": "area", "equals": "Other"}},
            {"key": "city", "label": "City / District", "required": True},
            {"key": "postal_code", "label": "Postal Code (optional)", "required": False, "pattern": r"^[0-9]{5}$"},
        ],
        "example": "Building 12, Queen Rania St., Amman",
    },
    "US": {
        "fields": [
            {"key": "address_line1", "label": "Street address", "required": True},
            {"key": "address_line2", "label": "Apt, suite, etc. (optional)", "required": False},
            {"key": "city", "label": "City", "required": True},
            {"key": "state", "label": "State", "required": True, "type": "select",
             "options": ["AL","AK","AZ","AR","CA","CO","CT","DC","DE","FL","GA","HI","IA","ID","IL","IN","KS","KY","LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","PR","RI","SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","WY"]},
            {"key": "postal_code", "label": "ZIP / ZIP+4", "required": True, "pattern": r"^[0-9]{5}(-[0-9]{4})?$"},
        ],
        "example": "1600 Pennsylvania Ave NW, Washington",
    },
    "AE": {
        "fields": [
            {"key": "address_line1", "label": "Building / Street", "required": True},
            {"key": "emirate", "label": "Emirate", "required": True, "type": "select",
             "options": ["Abu Dhabi","Dubai","Sharjah","Ajman","Umm Al Quwain","Ras Al Khaimah","Fujairah"]},
            {"key": "area", "label": "Area / Community", "required": True},
            {"key": "postal_code", "label": "P.O. Box (optional)", "required": False},
        ],
        "example": "Office 1003, XYZ Tower, Business Bay, Dubai",
    },
    "UK": {
        "fields": [
            {"key": "address_line1", "label": "Building and street", "required": True},
            {"key": "address_line2", "label": "Address line 2 (optional)", "required": False},
            {"key": "city", "label": "Town / City", "required": True},
            {"key": "postal_code", "label": "Postcode", "required": True, "pattern": r"^[A-Za-z0-9 ]{5,8}$"},
        ],
        "example": "10 Downing St, London",
    },
    # Fallback
    "ZZ": {
        "fields": [
            {"key": "address_line1", "label": "Address line 1", "required": True},
            {"key": "address_line2", "label": "Address line 2 (optional)", "required": False},
            {"key": "city", "label": "City / Locality", "required": True},
            {"key": "province", "label": "State / Province / Region", "required": False},
            {"key": "postal_code", "label": "Postal / ZIP Code", "required": False},
        ],
        "example": "",
    },
}

# -----------------------------
# Phone validation helpers
# -----------------------------
E164_RE = re.compile(r"^\+\d{8,15}$")
try:
    import phonenumbers  # type: ignore
except Exception:
    phonenumbers = None

def _normalize_phone(e164: str | None) -> str | None:
    if not e164:
        return None
    e164 = e164.strip()
    if phonenumbers:
        try:
            num = phonenumbers.parse(e164, None)
            if phonenumbers.is_valid_number(num):
                return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
            return None
        except Exception:
            return None
    # Fallback simple E.164 validation
    return e164 if E164_RE.match(e164) else None

# -----------------------------
# Address validation (server mirror)
# -----------------------------
def _validate_address(country_code: str, data: dict):
    code = (country_code or "").upper()
    rules = ADDRESS_RULES.get(code, ADDRESS_RULES["ZZ"])

    # Required
    for f in rules.get("fields", []):
        if f.get("required"):
            if not (data.get(f["key"]) or "").strip():
                raise ValueError(f'Please provide {f["label"]}.')

    # Conditional requiredIf
    for f in rules.get("fields", []):
        cond = f.get("requiredIf")
        if cond:
            trigger_val = (data.get(cond["field"]) or "").strip()
            if trigger_val == cond.get("equals"):
                if not (data.get(f["key"]) or "").strip():
                    raise ValueError(f'Please provide {f["label"]}.')

    # Patterns
    for f in rules.get("fields", []):
        pat = f.get("pattern")
        val = (data.get(f["key"]) or "").strip()
        if pat and val:
            if not re.compile(pat).match(val):
                raise ValueError(f'Invalid {f["label"]}.')

# -----------------------------
# Tiny JSON APIs for the frontend
# -----------------------------
def country_list_api(request):
    """
    Returns only ship-to countries. Add "Other" in the UI if you want,
    but server will reject non-SHIP_TO selections on POST.
    """
    data = [{"code": code, "name": dict(countries)[code]} for code in SHIP_TO]
    return JsonResponse({"countries": data})

def address_schema_api(request, code: str):
    code = (code or "ZZ").upper()
    schema = ADDRESS_RULES.get(code, ADDRESS_RULES["ZZ"])
    return JsonResponse(schema)

# -----------------------------
# Utilities
# -----------------------------
def _post_first(request, *keys):
    for k in keys:
        v = request.POST.get(k)
        if v:
            return v
    return ""

def _send_emails_async(request, order):
    def task():
        try:
            _email_order_confirmation(request, order)
            _email_admin_new_order(request, order)
        except Exception:
            # swallow email exceptions so checkout never hangs
            pass
    threading.Thread(target=task, daemon=True).start()

# -----------------------------
# Checkout view
# -----------------------------
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect, render
# If _promo_valid_for_db lives in this module, you're set.
# If you put it elsewhere, import it: from .promos import _promo_valid_for_db
# Also make sure money_filter exists as shown earlier.
# views.py
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

from .models import Order, OrderItem, PromoCode  # PromoCode only needed for usage bump

# Assumes these helpers/consts already exist in your codebase:
# _get_cart, _items_and_subtotal, _post_first, _normalize_phone,
# _validate_address, _format_address_text, _send_emails_async,
# _promo_valid_for_db, SHIP_TO, SHIP_TO_COUNTRIES, CART_KEY


def checkout(request):
    """
    Checkout — creates Order + OrderItems, sends emails async, clears cart.
    - Enforces ship-to countries (Middle East + USA).
    - Validates phone strictly (E.164).
    - Country-aware address validation (PH/JO/US/AE/UK + fallback).
    - Applies DB-configured promo codes (percent or flat), with country / dates / caps.
    - Stores a normalized address object into `Order.shipping_address` if present.
    """
    cart = _get_cart(request.session)
    items, subtotal = _items_and_subtotal(cart)

    if request.method == "POST":
        # Contact
        full_name = (request.POST.get("full_name") or "").strip()
        raw_phone = _post_first(request, "phone_e164", "phone", "phone_display")
        phone     = _normalize_phone(raw_phone)
        email     = (request.POST.get("email") or "").strip()
        notes     = (request.POST.get("notes") or "").strip()

        # Country (ISO-2 like "PH", "JO", "US", "AE", "UK")
        country = (request.POST.get("country") or "").strip().upper()

        # Shipping availability
        if country not in SHIP_TO:
            messages.error(request, "Sorry, we currently ship only to the Middle East and USA.")
            return render(request, "checkout.html", {
                "items": items, "subtotal": subtotal, "ship_to_countries": SHIP_TO_COUNTRIES,
            })

        # Collect all possible address bits (schema defines required ones)
        addr = {
            "address_line1": request.POST.get("address_line1"),
            "address_line2": request.POST.get("address_line2"),
            "barangay":      request.POST.get("barangay"),
            "city":          request.POST.get("city"),
            "province":      request.POST.get("province"),
            "postal_code":   request.POST.get("postal_code"),
            "area":          request.POST.get("area"),
            "area_other":    request.POST.get("area_other"),
            "state":         request.POST.get("state"),
            "county":        request.POST.get("county"),
            "emirate":       request.POST.get("emirate"),
        }

        shipping_method = (request.POST.get("shipping") or "standard").strip().lower()
        payment_method  = (request.POST.get("payment")  or "cod").strip().lower()

        # Basic cart check
        if not items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        # Core field checks
        if not full_name:
            messages.error(request, "Please enter your full name.")
            return render(request, "checkout.html", {
                "items": items, "subtotal": subtotal, "ship_to_countries": SHIP_TO_COUNTRIES
            })
        if not phone:
            messages.error(request, "Please enter a valid phone number (e.g., +962 7X XXX XXXX).")
            return render(request, "checkout.html", {
                "items": items, "subtotal": subtotal, "ship_to_countries": SHIP_TO_COUNTRIES
            })

        # Country-aware address validation
        try:
            _validate_address(country, addr)
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, "checkout.html", {
                "items": items, "subtotal": subtotal, "ship_to_countries": SHIP_TO_COUNTRIES
            })

        # Shipping cost (free/standard/express)
        if shipping_method in ("standard", "free"):
            shipping_cost = Decimal("0.00")
        elif shipping_method == "express":
            shipping_cost = Decimal("299.00")
        else:
            shipping_cost = Decimal("0.00")

        # ---- Promo (server truth) ------------------------------------------
        # Accept either 'promo' (recommended) or legacy 'promo_code'
        promo_code = (request.POST.get("promo") or request.POST.get("promo_code") or "").strip().upper()
        discount_total = Decimal("0.00")
        promo_label = ""

        if promo_code:
            disc, msg = _promo_valid_for_db(promo_code, subtotal=subtotal, country=country)
            if disc is not None:
                discount_total = (disc or Decimal("0.00")).quantize(Decimal("0.01"))
                promo_label = msg or promo_code
            else:
                # UI tries to validate, but server is source of truth
                messages.warning(request, msg or "Promo code couldn’t be applied.")

        grand_total = (subtotal + shipping_cost - discount_total).quantize(Decimal("0.01"))

        # Create the order (only set fields your model actually has)
        order_kwargs = dict(
            full_name=full_name,
            phone=phone,
            email=email,
            shipping_method=shipping_method,
            payment_method=payment_method,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            discount_total=discount_total,
            grand_total=grand_total,
            status="pending",
        )

        # Optional fields if present on the model
        try:
            probe = Order()  # lightweight instance to check attrs
            if hasattr(probe, "country"):
                order_kwargs["country"] = country
            if hasattr(probe, "shipping_address"):
                order_kwargs["shipping_address"] = {k: (v or "").strip() for k, v in addr.items() if v}
            if hasattr(probe, "shipping_address_text"):
                order_kwargs["shipping_address_text"] = _format_address_text(country, addr)
            if hasattr(probe, "notes"):
                order_kwargs["notes"] = notes
            if hasattr(probe, "promo_code"):
                order_kwargs["promo_code"] = promo_code or None
            if hasattr(probe, "promo_label"):
                order_kwargs["promo_label"] = promo_label or ""
        except Exception:
            pass

        with transaction.atomic():
            order = Order.objects.create(**order_kwargs)

            # Line items
            for row in items:
                p = row["product"]
                qty = int(row["qty"])
                line_total = (p.price * qty).quantize(Decimal("0.01"))
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    name=p.name,
                    unit_price=p.price,
                    quantity=qty,
                    line_total=line_total,
                )

            # Best-effort: increment promo usage if applied
            if promo_code and discount_total > 0:
                try:
                    from django.db.models import F
                    # Support either 'used_count' or 'usage_count' field names
                    fields = {f.name for f in PromoCode._meta.get_fields()}
                    qs = PromoCode.objects.filter(code__iexact=promo_code)
                    if "used_count" in fields:
                        qs.update(used_count=F("used_count") + 1)
                    elif "usage_count" in fields:
                        qs.update(usage_count=F("usage_count") + 1)
                except Exception:
                    pass

        # Clear cart ASAP
        request.session[CART_KEY] = {}
        request.session.modified = True

        # Send emails AFTER commit, in background
        transaction.on_commit(lambda: _send_emails_async(request, order))

        messages.success(request, "Order placed! We’ve emailed your confirmation.")
        return redirect(f"/thanks/?o={order.order_number}")

    # GET
    return render(request, "checkout.html", {
        "items": items,
        "subtotal": subtotal,
        "ship_to_countries": SHIP_TO_COUNTRIES,
    })


# -----------------------------
# Pretty label for shipping_address_text
# -----------------------------
def _format_address_text(country: str, a: dict) -> str:
    country = (country or "").upper()
    if country == "PH":
        parts = [
            a.get("address_line1"),
            f"Brgy. {a.get('barangay')}" if a.get("barangay") else None,
            a.get("city"),
            a.get("province"),
            a.get("postal_code"),
            "Philippines",
        ]
    elif country == "JO":
        area = a.get("area_other") if (a.get("area") == "Other") else a.get("area")
        parts = [a.get("address_line1"), area, a.get("city"), a.get("postal_code"), "Jordan"]
    elif country == "US":
        parts = [a.get("address_line1"), a.get("address_line2"),
                 f"{a.get('city')}, {a.get('state')} {a.get('postal_code')}", "United States"]
    elif country == "AE":
        parts = [a.get("address_line1"), a.get("area"), a.get("emirate"), "United Arab Emirates"]
    elif country == "UK":
        parts = [a.get("address_line1"), a.get("address_line2"), a.get("city"), a.get("postal_code"), "United Kingdom"]
    else:
        # Fallback
        parts = [a.get("address_line1"), a.get("address_line2"), a.get("city"), a.get("province"), a.get("postal_code"),
                 dict(countries).get(country, country)]
    return ", ".join([p.strip() for p in parts if p and str(p).strip()])


def thanks(request):
    order_number = request.GET.get("o", "")
    return render(request, "thanks.html", {"order_number": order_number})


# =======================
# Order Status / Detail
# =======================
# views.py
import re
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render
from django.db.models import Prefetch

from .models import Order


ORDER_TTL_SECONDS = 600        # rate-limit window (10 minutes)
ORDER_MAX_TRIES   = 25         # max attempts per IP per window


def _normalize_order_number(raw: str) -> str:
    """
    Normalize common inputs:
    - trims, uppercases
    - allows 'SH482931', 'sh-482931', 'SH - 482931'
    - returns 'SH-482931' if pattern matches; otherwise returns cleaned string
    """
    s = (raw or "").strip().upper()
    # Remove surrounding spaces and collapse internal spaces around hyphen
    s = re.sub(r"\s+", "", s)
    # If starts with SH and then digits (with or without hyphen)
    m = re.fullmatch(r"SH-?(\d{6,})", s)
    if m:
        return f"SH-{m.group(1)}"
    # Fallback: strip non-alnum and retry
    alt = re.sub(r"[^A-Z0-9]", "", s)
    m2 = re.fullmatch(r"SH(\d{6,})", alt)
    return f"SH-{m2.group(1)}" if m2 else s


def _emails_match(a: str | None, b: str | None) -> bool:
    return (a or "").strip().lower() == (b or "").strip().lower()


def order_status(request):
    """
    Public lookup: order number + optional email.
    - If email is provided: must match (case-insensitive).
    - If email is blank: allow lookup by order number only (set limited_view=True).
    - Order number normalization: handles spaces, lowercase, and missing hyphen.
    - Adds honeypot + basic per-IP rate limiting to deter enumeration.
    """
    context = {}
    template = "order_status.html"  # change if your template path differs

    if request.method != "POST":
        return render(request, template, context)

    # --- Honeypot (bot trap) ---
    if (request.POST.get("website") or "").strip():
        # Pretend it's just not found
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # --- Simple per-IP rate limit ---
    ip = (request.META.get("HTTP_X_FORWARDED_FOR", "") or "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
    if ip:
        key = f"order_status:tries:{ip}"
        try_count = (cache.get(key) or 0) + 1
        cache.set(key, try_count, ORDER_TTL_SECONDS)
        if try_count > ORDER_MAX_TRIES:
            messages.error(request, "Too many attempts. Please try again later.")
            return render(request, template, context)

    raw_order_number = request.POST.get("order_number") or ""
    input_email = (request.POST.get("email") or "").strip().lower()

    order_number = _normalize_order_number(raw_order_number)

    # Quick format sanity—optional but nice UX
    if not re.fullmatch(r"SH-\d{6,}", order_number):
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # Fetch order (case-insensitive), with items prefetched
    order = (
        Order.objects
        .prefetch_related(Prefetch("items"))
        .filter(order_number__iexact=order_number)
        .first()
    )

    if not order:
        # No hint whether order number or email is wrong
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # If email provided, it must match
    if input_email:
        candidates = [
            (order.email or ""),
            getattr(getattr(order, "user", None), "email", "") or "",
        ]
        if any(_emails_match(e, input_email) for e in candidates):
            context["order"] = order
            context["limited_view"] = False
            return render(request, template, context)
        # Mismatch → generic error
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # No email → allow limited view; template can hide sensitive fields if desired
    context["order"] = order
    context["limited_view"] = True
    messages.info(request, "For full details, add the email used at checkout.")
    return render(request, template, context)


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
    - Sends an admin notification email (via Resend through _safe_send_mail).
    - Sends a branded HTML auto-reply to the user (if they provided a valid email).
    - Redirects to 'contact_thanks' on success.
    """
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        message = (request.POST.get("message") or "").strip()

        # Basic validation
        if not name or not message:
            messages.error(request, "Please provide your name and message.")
            return render(request, "contact.html", {
                "name": name,
                "email": email,
                "message_text": message
            })

        # Validate email if provided (optional field)
        user_email_ok = False
        if email:
            try:
                validate_email(email)
                user_email_ok = True
            except ValidationError:
                user_email_ok = False  # skip auto-reply; still accept the form

        # --- Admin notification ---
        admin_to = getattr(settings, "CONTACT_TO", None) or getattr(settings, "DEFAULT_FROM_EMAIL", None)
        if admin_to:
            subject = f"New contact from {name}"
            body = f"Name: {name}\nEmail: {email or 'N/A'}\n\nMessage:\n{message}"
            ok = _safe_send_mail(
                subject=subject,
                text_body=body,
                from_email=None,                # Resend uses settings.RESEND['FROM']
                to_list=[admin_to],
                html_body=None
            )
            if not ok:
                messages.warning(
                    request,
                    "Your message was received, but we couldn’t notify our team by email. We’ll still follow up."
                )

        # --- Auto-reply to sender (HTML + plain text fallback) ---
        if user_email_ok:
            try:
                context = {
                    "name": name,
                    "user_message": message,
                    "products_url": request.build_absolute_uri("/products/"),
                    "order_status_url": request.build_absolute_uri("/order-status/"),
                    "support_email": admin_to or (getattr(settings, "DEFAULT_FROM_EMAIL", "") or ""),
                }
                html = render_to_string("emails/contact_autoreply.html", context)
                text = strip_tags(html)

                _safe_send_mail(
                    subject="Thanks for contacting SHARP — We’re on it",
                    text_body=text,
                    from_email=None,             # Resend uses configured FROM
                    to_list=[email],
                    html_body=html
                )
            except Exception as e:
                # Don't break UX if email fails
                logger.exception("Auto-reply send failed: %s", e)

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
        "items": list(order.items.all()),   # or order.orderitem_set.all()
        "request": request,
        "order_status_url": request.build_absolute_uri(
            getattr(getattr(settings, "ORDER_STATUS_URL", None), "strip", lambda: "")()
        ) if getattr(settings, "ORDER_STATUS_URL", None) else request.build_absolute_uri(
            "/order-status/"
        ),
    }

    subject   = f"Your SHARP Order {order.order_number}"
    text_body = render_to_string("emails/order_confirmation.txt", context)
    html_body = render_to_string("emails/order_confirmation.html", context)

    ok = _safe_send_mail(
        subject=subject,
        text_body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to_list=[order.email],
        html_body=html_body,
        extra_headers={
            "Reply-To": getattr(settings, "CONTACT_RECEIVER_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")
        },
    )
    if not ok:
        messages.warning(
            request,
            "Order placed, but we couldn’t send your confirmation email. We’ll resend shortly."
        )


def _email_admin_new_order(request, order: Order):
    admin_email = getattr(settings, "ADMIN_ORDER_EMAIL", None)
    if not admin_email:
        return

    try:
        items_qs = order.items.all()
    except Exception:
        items_qs = order.orderitem_set.all()

    context = {"order": order, "items": items_qs, "request": request}

    subject   = f"New Order: {order.order_number}"
    text_body = render_to_string("emails/admin_new_order.txt", context)

    _safe_send_mail(
        subject=subject,
        text_body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to_list=[admin_email],
    )




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

def _cart_json(session, request):
    """Serialize the cart to JSON for AJAX drawer (now with server-formatted strings)."""
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
            "price": f"{p.price:.2f}",                     # numeric (string)
            "line_total": f"{line_total:.2f}",             # numeric (string)
            "line_total_display": money_filter(line_total, request),  # ✅ formatted
            "slug": p.slug,
        })

    return {
        "count": sum(i["qty"] for i in items),
        "subtotal": f"{subtotal:.2f}",                         # numeric (string)
        "subtotal_display": money_filter(subtotal, request),   # ✅ formatted
        "items": items,
    }


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


# =======================
# Pages
# =======================
# myApp/views.py
from django.db.models import Prefetch
from .models import Product, Order, OrderItem, ProductComponent  # + ProductComponent

def home(request):
    featured = (
        Product.objects
        .filter(is_active=True, is_bundle=False)
        .order_by('name')[:4]
    )

    bundle_links = Prefetch(
        'component_links',
        queryset=ProductComponent.objects.select_related('component')
    )
    bundles = (
        Product.objects
        .filter(is_active=True, is_bundle=True)
        .prefetch_related(bundle_links)
        .order_by('name')[:4]
    )

    return render(request, "home.html", {
        "featured": featured,
        "bundles": bundles,   # ← new
    })



# myApp/views.py
from django.db.models import Prefetch
from .models import Product, ProductComponent  # add ProductComponent

def product_list(request):
    q_type = (request.GET.get("type") or "all").lower()

    qs = Product.objects.filter(is_active=True).order_by("name")
    if q_type == "bundle":
        qs = qs.filter(is_bundle=True)
    elif q_type == "single":
        qs = qs.filter(is_bundle=False)

    # Prefetch bundle components only if we’re showing any bundles
    if qs.filter(is_bundle=True).exists():
        qs = qs.prefetch_related(
            Prefetch("component_links", queryset=ProductComponent.objects.select_related("component"))
        )

    return render(request, "products.html", {"products": qs, "q_type": q_type})


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
        data = _cart_json(request.session, request)  # ← pass request
        return JsonResponse({"ok": True, "cart": data, "message": f"Added {escape(product.name)} x{qty}"})

    messages.success(request, f"Added {product.name} (x{qty}) to cart.")
    return redirect("cart")


@require_POST
def cart_update(request, product_id):
    """
    Update quantity for a cart line (supports AJAX).
    POST: qty (>=1); if qty <= 0, removes the item.
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
        return JsonResponse({"ok": True, "cart": _cart_json(request.session, request)})  # ← pass request

    return redirect("cart")


@require_POST
def cart_remove(request, product_id):
    """Remove item from cart (supports AJAX)."""
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    request.session.modified = True

    if _is_ajax(request):
        data = _cart_json(request.session, request)  # ← pass request
        return JsonResponse({"ok": True, "cart": data})

    messages.info(request, "Item removed from cart.")
    return redirect("cart")


def cart_summary_json(request):
    """Return JSON summary for drawer refresh."""
    return JsonResponse({"ok": True, "cart": _cart_json(request.session, request)})  # ← pass request



def thanks(request):
    order_number = request.GET.get("o", "")
    return render(request, "thanks.html", {"order_number": order_number})


# =======================
# Order Status / Detail
# =======================
# views.py
import re
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render
from django.db.models import Prefetch

from .models import Order


ORDER_TTL_SECONDS = 600        # rate-limit window (10 minutes)
ORDER_MAX_TRIES   = 25         # max attempts per IP per window


def _normalize_order_number(raw: str) -> str:
    """
    Normalize common inputs:
    - trims, uppercases
    - allows 'SH482931', 'sh-482931', 'SH - 482931'
    - returns 'SH-482931' if pattern matches; otherwise returns cleaned string
    """
    s = (raw or "").strip().upper()
    # Remove surrounding spaces and collapse internal spaces around hyphen
    s = re.sub(r"\s+", "", s)
    # If starts with SH and then digits (with or without hyphen)
    m = re.fullmatch(r"SH-?(\d{6,})", s)
    if m:
        return f"SH-{m.group(1)}"
    # Fallback: strip non-alnum and retry
    alt = re.sub(r"[^A-Z0-9]", "", s)
    m2 = re.fullmatch(r"SH(\d{6,})", alt)
    return f"SH-{m2.group(1)}" if m2 else s


def _emails_match(a: str | None, b: str | None) -> bool:
    return (a or "").strip().lower() == (b or "").strip().lower()


def order_status(request):
    """
    Public lookup: order number + optional email.
    - If email is provided: must match (case-insensitive).
    - If email is blank: allow lookup by order number only (set limited_view=True).
    - Order number normalization: handles spaces, lowercase, and missing hyphen.
    - Adds honeypot + basic per-IP rate limiting to deter enumeration.
    """
    context = {}
    template = "order_status.html"  # change if your template path differs

    if request.method != "POST":
        return render(request, template, context)

    # --- Honeypot (bot trap) ---
    if (request.POST.get("website") or "").strip():
        # Pretend it's just not found
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # --- Simple per-IP rate limit ---
    ip = (request.META.get("HTTP_X_FORWARDED_FOR", "") or "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
    if ip:
        key = f"order_status:tries:{ip}"
        try_count = (cache.get(key) or 0) + 1
        cache.set(key, try_count, ORDER_TTL_SECONDS)
        if try_count > ORDER_MAX_TRIES:
            messages.error(request, "Too many attempts. Please try again later.")
            return render(request, template, context)

    raw_order_number = request.POST.get("order_number") or ""
    input_email = (request.POST.get("email") or "").strip().lower()

    order_number = _normalize_order_number(raw_order_number)

    # Quick format sanity—optional but nice UX
    if not re.fullmatch(r"SH-\d{6,}", order_number):
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # Fetch order (case-insensitive), with items prefetched
    order = (
        Order.objects
        .prefetch_related(Prefetch("items"))
        .filter(order_number__iexact=order_number)
        .first()
    )

    if not order:
        # No hint whether order number or email is wrong
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # If email provided, it must match
    if input_email:
        candidates = [
            (order.email or ""),
            getattr(getattr(order, "user", None), "email", "") or "",
        ]
        if any(_emails_match(e, input_email) for e in candidates):
            context["order"] = order
            context["limited_view"] = False
            return render(request, template, context)
        # Mismatch → generic error
        messages.error(request, "We couldn’t find an order with those details.")
        return render(request, template, context)

    # No email → allow limited view; template can hide sensitive fields if desired
    context["order"] = order
    context["limited_view"] = True
    messages.info(request, "For full details, add the email used at checkout.")
    return render(request, template, context)


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
        "items": list(order.items.all()),
        "request": request,
    }
    subject = f"Your SHARP Order {order.order_number}"
    text_body = render_to_string("emails/order_confirmation.txt", context)
    html_body = render_to_string("emails/order_confirmation.html", context)

    ok = _safe_send_mail(
        subject=subject,
        text_body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to_list=[order.email],
        html_body=html_body,
        extra_headers={"Reply-To": getattr(settings, "CONTACT_RECEIVER_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")},
    )
    if not ok:
        # Don’t block UX—just let the user know softly.
        messages.warning(request, "Order placed, but we couldn’t send your confirmation email. We’ll resend shortly.")


def _email_admin_new_order(request, order: Order):
    """Notify admin of a new order (non-blocking)."""
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

    _safe_send_mail(
        subject=subject,
        text_body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to_list=[admin_email],
        # If you add an HTML template later, pass html_body=...
    )



def blog_sample(request):
    return render(request, "blog/post_detail_sample.html")


from django.shortcuts import get_object_or_404, render
from .models import Post

def blog_detail(request, slug):
    post = get_object_or_404(Post.objects.prefetch_related("blocks"), slug=slug)
    return render(request, "blog/post_detail.html", {"post": post})

def blog_index(request):
    posts = Post.objects.order_by("-published_at")
    return render(request, "blog/post_list.html", {"posts": posts})


import json, re
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import timezone
from django.core.cache import cache
from .models import Subscriber

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return (xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR"))

@require_POST
@csrf_protect
def subscribe_create(request):
    """
    Create (or 'upsert') a subscriber. Idempotent on email.
    Accepts form-encoded or JSON. Returns JSON.
    Simple rate-limit: 1 hit / 5s per IP.
    """
    ip = _client_ip(request) or "0.0.0.0"
    key = f"subrl:{ip}"
    if cache.get(key):
        return JsonResponse({"ok": False, "error": "Too many requests, please try again in a moment."}, status=429)
    cache.set(key, 1, 5)

    # Parse body
    if request.content_type and "application/json" in request.content_type:
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"ok": False, "error": "Bad JSON."}, status=400)
        email = (body.get("email") or "").strip().lower()
        name  = (body.get("name")  or "").strip()
        source = (body.get("source") or "footer_form").strip()
        honeypot = (body.get("company") or "").strip()
    else:
        email = (request.POST.get("email") or "").strip().lower()
        name  = (request.POST.get("name")  or "").strip()
        source = (request.POST.get("source") or "footer_form").strip()
        honeypot = (request.POST.get("company") or "").strip()

    if honeypot:
        return JsonResponse({"ok": True, "message": "Thanks!"})  # silent success for bots

    if not EMAIL_RE.match(email):
        return JsonResponse({"ok": False, "error": "Please enter a valid email."}, status=400)

    # Upsert behavior
    sub, created = Subscriber.objects.get_or_create(email=email, defaults={
        "name": name, "source": source, "ip": ip, "ua": request.META.get("HTTP_USER_AGENT","")[:500]
    })
    if not created:
        # Reactivate if previously unsubscribed; update name/source if provided
        changed = False
        if sub.unsubscribed_at:
            sub.unsubscribed_at = None
            changed = True
        if name and sub.name != name:
            sub.name = name; changed = True
        if source and sub.source != source:
            sub.source = source; changed = True
        if changed:
            sub.save(update_fields=["unsubscribed_at", "name", "source"])

    return JsonResponse({"ok": True, "created": created, "email": sub.email})


from .models import PromoCode
# views.py
import re
from .models import PromoCode

def _normalize_code(s: str) -> str:
    # Uppercase and strip anything that isn't A–Z or 0–9
    return re.sub(r'[^A-Z0-9]', '', (s or '').upper())

def _promo_lookup(code):
    c = (code or "").strip().upper()
    if not c:
        return None
    return PromoCode.objects.filter(code__iexact=c).first()

def _promo_valid_for_db(code, *, subtotal: Decimal, country: str | None):
    """
    Returns (discount_decimal, label) or (None, error_text)
    """
    promo = _promo_lookup(code)
    if not promo:
        return (None, "Promo code not recognized.")
    if not promo.is_live():
        return (None, "This promo is not active.")

    # Country allow-list
    allow = promo.countries()
    if allow and (country or "").upper() not in allow:
        return (None, "This promo doesn’t apply in your country.")

    # Minimum subtotal
    min_needed = promo.min_subtotal or Decimal("0")
    if subtotal < min_needed:
        return (None, f"Minimum order of {_money(min_needed)} required.")

    # Compute discount
    if promo.type == "percent":
        # promo.value is percent e.g. 10 for 10%
        disc = (subtotal * (promo.value or 0) / Decimal("100")).quantize(Decimal("0.01"))
    elif promo.type == "flat":
        disc = max(Decimal("0.00"), (promo.value or 0)).quantize(Decimal("0.01"))
    else:
        return (None, "Invalid promo configuration.")

    # Cap
    if promo.max_discount:
        disc = min(disc, promo.max_discount)

    if disc <= 0:
        return (None, "This promo doesn’t apply to your cart.")
    return (disc, promo.description or promo.code)


# at the top of views.py (with your other imports)
from django.views.decorators.http import require_GET

@require_GET
def apply_promo_json(request):
    """
    GET /api/promo/apply?code=SHARP2025&country=JO
    Server recomputes subtotal from the *current cart* (no client math),
    applies promo, and returns display strings already formatted in the
    request currency via your money filter.
    """
    code = (request.GET.get("code") or "").strip()
    country = (request.GET.get("country") or "").strip().upper()

    # Subtotal from session cart (source currency = PRICE_SOURCE_CURRENCY)
    cart = _get_cart(request.session)
    _, subtotal = _items_and_subtotal(cart)
    if subtotal < 0:
        subtotal = Decimal("0.00")

    disc, msg = _promo_valid_for_db(code, subtotal=subtotal, country=country)
    if disc is None:
        return JsonResponse({"ok": False, "error": msg or "Promo not valid."}, status=400)

    discount = (disc or Decimal("0.00")).quantize(Decimal("0.01"))
    grand_total = (subtotal - discount).quantize(Decimal("0.01"))

    promo_obj = _promo_lookup(code)

    return JsonResponse({
        "ok": True,
        # amounts as numbers (strings) in source currency, if you need them
        "subtotal": str(subtotal.quantize(Decimal("0.01"))),
        "grand_total": str(grand_total),
        "amount": str(discount),

        # pretty strings already formatted (and converted if needed)
        "subtotal_display": _money(subtotal, request),
        "grand_total_display": _money(grand_total, request),
        "amount_display": _money(discount, request),

        "label": msg or (promo_obj.description if promo_obj else code.upper()),
        "code": (promo_obj.code if promo_obj else code.upper()),
    })
