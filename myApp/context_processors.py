from decimal import Decimal

CART_KEY = "cart"

def cart(request):
    cart = request.session.get(CART_KEY, {}) or {}
    count = sum(int(q) for q in cart.values())
    subtotal = Decimal("0.00")
    # (optional subtotal, handy for badge/tooltips)
    from .models import Product
    for pid, q in cart.items():
        p = Product.objects.filter(id=int(pid), is_active=True).first()
        if p:
            subtotal += p.price * int(q)
    return {"cart_count": count, "cart_subtotal": subtotal}

from .models import Order, Product

def dashboard_counts(request):
    """
    Adds:
      - nav_counts: tiny badges (pending orders, inactive products)
      - nav_state: booleans for which tab is active
    """
    path = (request.path or "")
    if not path.startswith("/dashboard"):
        # Header still renders; just no badges/active highlighting
        return {"nav_counts": {}, "nav_state": {}}

    # counts (super cheap)
    try:
        pending_orders = Order.objects.filter(status="0").count()
    except Exception:
        pending_orders = 0

    try:
        inactive_products = Product.objects.filter(is_active=False).count()
    except Exception:
        inactive_products = 0

    # which tab is active?
    rm = getattr(request, "resolver_match", None)
    url_name = getattr(rm, "url_name", "") if rm else ""

    orders_names   = {"dashboard_order_list", "dashboard_order_detail"}
    products_names = {"dashboard_product_list", "dashboard_product_new", "dashboard_product_edit"}

    nav_state = {
        "is_home":     (url_name == "dashboard_home"),
        "is_orders":   (url_name in orders_names),
        "is_products": (url_name in products_names),
        "is_promos":   (url_name == "dashboard_promo_list"),
    }

    return {
        "nav_counts": {
            "orders_pending": pending_orders,
            "products_inactive": inactive_products,
        },
        "nav_state": nav_state,
    }
