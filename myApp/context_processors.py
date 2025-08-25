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
