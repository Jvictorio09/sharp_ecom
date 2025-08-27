# app/models.py
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.core.validators import MinValueValidator

# ============== Product ==============
class Product(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True, db_index=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    image_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional: simple gallery support (store a comma-separated list of URLs or switch to JSONField)
    gallery_csv = models.TextField(blank=True, help_text="Comma-separated image URLs", default="")

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.name

    @property
    def gallery(self):
        # convenience accessor used by the template (product_detail)
        if not self.gallery_csv:
            return []
        return [u.strip() for u in self.gallery_csv.split(",") if u.strip()]

    def save(self, *args, **kwargs):
        # Auto-generate unique slug if missing or name changed
        if not self.slug:
            base = slugify(self.name) or "product"
            slug = base
            n = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


# ============== Remove these if staying on session-cart ==============
# Your current views use the session for cart storage.
# If you plan to migrate to a DB-backed cart, keep these and I’ll refactor views.
# Otherwise, delete Cart & CartItem to avoid confusion.

# class Cart(models.Model):
#     session_key = models.CharField(max_length=40, db_index=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     def __str__(self): return f"Cart {self.id}"
#     def total(self): return sum(item.subtotal() for item in self.items.all())

# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.PROTECT)
#     quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
#     def __str__(self): return f"{self.quantity} x {self.product.name}"
#     def subtotal(self): return (self.product.price * self.quantity).quantize(Decimal("0.01"))


# ============== Orders ==============
def generate_order_number():
    # e.g. SH-482931
    return f"SH-{get_random_string(6, allowed_chars='0123456789')}"

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Customer
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    address_line1 = models.TextField()
    city = models.CharField(max_length=80, blank=True)
    province = models.CharField(max_length=80, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    # Choices
    shipping_method = models.CharField(max_length=20, default="standard")  # 'standard' | 'express'
    payment_method = models.CharField(max_length=20, default="cod")        # 'cod' (for now)

    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # Meta
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.order_number} — {self.full_name}"

    def save(self, *args, **kwargs):
        # Ensure unique order number (rare collision guard)
        if not self.order_number:
            candidate = generate_order_number()
            while Order.objects.filter(order_number=candidate).exists():
                candidate = generate_order_number()
            self.order_number = candidate
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"{self.name} × {self.quantity} ({self.order.order_number})"
