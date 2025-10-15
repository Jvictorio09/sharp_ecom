# myApp/models.py
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.core.validators import MinValueValidator

# -----------------------------
# Products (with bundle support)
# -----------------------------
class Product(models.Model):
    name = models.CharField(max_length=150, unique=True)
    sku = models.CharField(max_length=64, blank=True, null=True, db_index=True) 
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

    # Simple gallery via CSV (optional)
    gallery_csv = models.TextField(blank=True, help_text="Comma-separated image URLs", default="")

    # Bundle flags/relations
    is_bundle = models.BooleanField(
        default=False,
        help_text="Mark as True if this product is a package/bundle."
    )
    free_delivery = models.BooleanField(
        default=False,
        help_text="If True, this product qualifies the order for free delivery."
    )

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
        if not self.gallery_csv:
            return []
        return [u.strip() for u in self.gallery_csv.split(",") if u.strip()]

    def component_rows(self):
        """List of ProductComponent rows for this bundle (empty for singles)."""
        if not self.is_bundle:
            return []
        return list(self.component_links.select_related('component').all())

    def save(self, *args, **kwargs):
        # Auto-generate unique slug if missing
        if not self.slug:
            base = slugify(self.name) or "product"
            slug = base
            n = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductComponent(models.Model):
    parent = models.ForeignKey(
        Product, related_name='component_links', on_delete=models.CASCADE
    )
    component = models.ForeignKey(
        Product, related_name='as_component_in', on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parent', 'component'], name='uniq_bundle_component')
        ]

    def __str__(self):
        return f"{self.parent.name} → {self.quantity}× {self.component.name}"


# -------------
# Orders
# -------------
def generate_order_number():
    # e.g. SH-482931
    return f"SH-{get_random_string(6, allowed_chars='0123456789')}"


class Order(models.Model):
    STATUS_CHOICES = [
        # Common checkpoints
        ("0",   "Created (awaiting courier)"), 
        ("60",  "Assign driver to pick up"),
        ("100", "Picked up by driver"),
        ("120", "Stored in warehouse"),
        ("130", "Out for delivery"),
        ("170", "Delivered to customer"),
        ("180", "Returned from customer"),
        ("190", "Item returned to returned shelf"),
        ("210", "Returned to shipper (RTO)"),

        # Special outbound / inbound
        ("121", "Departed to airport"),
        ("123", "Departed from origin – Outgoing"),
        ("51",  "Departed from origin – Incoming"),
        ("56",  "Arrival to gateway – Incoming"),
        ("57",  "Under clearance – Incoming"),
        ("58",  "Customs released – Incoming"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at   = models.DateTimeField(default=timezone.now)
    updated_at   = models.DateTimeField(auto_now=True)
    cancel_reason = models.TextField(blank=True, default="")

    # Customer info...
    full_name = models.CharField(max_length=120)
    phone     = models.CharField(max_length=40)
    email     = models.EmailField(blank=True)

    # Address + shipping fields...
    address_line1 = models.TextField()
    city          = models.CharField(max_length=80, blank=True)
    province      = models.CharField(max_length=80, blank=True)
    zip_code      = models.CharField(max_length=20, blank=True)

    country = models.CharField(max_length=2, blank=True, db_index=True)
    shipping_address = models.JSONField(blank=True, default=dict)
    shipping_address_text = models.TextField(blank=True, default="")

    shipping_method = models.CharField(max_length=20, default="standard")
    payment_method  = models.CharField(max_length=20, default="cod")

    subtotal       = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_cost  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    grand_total    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    notes  = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="0")
    
    # Zoho integration IDs (for fast lookups, avoid searching)
    zoho_data = models.JSONField(
        blank=True, 
        default=dict,
        help_text="Stores Zoho IDs: {salesorder_id, invoice_id, contact_id, synced_at}"
    )

    class Meta:
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.order_number} — {self.full_name}"

    def save(self, *args, **kwargs):
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
    cancel_reason = models.TextField(blank=True, default="")
    
    class Meta:
        indexes = [
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"{self.name} × {self.quantity} ({self.order.order_number})"


# myApp/models.py
class FxRate(models.Model):
    base = models.CharField(max_length=3, default="USD")
    quote = models.CharField(max_length=3)  # e.g., "PHP", "JOD", "AED"
    rate = models.DecimalField(max_digits=20, decimal_places=8)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("base","quote")



from django.db import models
from django.utils.text import slugify

class Post(models.Model):
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt      = models.TextField(blank=True)
    cover_image  = models.ImageField(upload_to="blog_covers/", blank=True, null=True)  # optional local
    cover_image_url = models.URLField(blank=True)  # ✅ remote (Cloudinary) URL
    published_at = models.DateTimeField(null=True, blank=True)
    author_name  = models.CharField(max_length=120, default="SHARP Editorial")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

BLOCK_TYPES = [
    ("paragraph","Paragraph"),
    ("heading","Heading"),
    ("image","Image"),
    ("gallery2","2-Image Row"),
    ("callout","Callout"),
    ("quote","Pull Quote"),
    ("product","Product Card"),
]

class PostBlock(models.Model):
    post    = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="blocks")
    order   = models.PositiveIntegerField(default=0)
    kind    = models.CharField(max_length=20, choices=BLOCK_TYPES)
    text    = models.TextField(blank=True)
    level   = models.CharField(max_length=10, blank=True)
    # Either local files…
    image1  = models.ImageField(upload_to="blog/", blank=True, null=True)
    image2  = models.ImageField(upload_to="blog/", blank=True, null=True)
    # …or remote URLs (Cloudinary)
    image1_url = models.URLField(blank=True)  # ✅
    image2_url = models.URLField(blank=True)  # ✅
    caption = models.CharField(max_length=200, blank=True)
    prod_query = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["order"]



from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True)
    source = models.CharField(max_length=64, blank=True, help_text="e.g. footer_form, checkout, popup")
    is_confirmed = models.BooleanField(default=False)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    # audit
    created_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    ua = models.TextField(blank=True)

    # optional: for double opt-in or future use
    confirm_token = models.CharField(max_length=48, blank=True, default="")

    def save(self, *args, **kwargs):
        if not self.confirm_token:
            self.confirm_token = get_random_string(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


from django.db import models
from django.utils import timezone
from decimal import Decimal

class PromoCode(models.Model):
    TYPE_CHOICES = (
        ("percent", "Percent (%)"),
        ("flat", "Flat amount"),
    )

    code = models.CharField(max_length=40, unique=True)           # e.g. "SHARP10"
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="percent")
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="If percent, 10 = 10%")
    description = models.CharField(max_length=255, blank=True)    # shown in dashboard / emails
    min_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    max_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    countries_csv = models.CharField(
        max_length=400, blank=True,
        help_text="Optional allow-list of ISO-2 codes, comma-separated (e.g. JO,AE,US). Leave blank for all."
    )
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Optional total usage cap")
    used_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    def countries(self):
        if not self.countries_csv.strip():
            return []
        return [c.strip().upper() for c in self.countries_csv.split(",") if c.strip()]

    def is_live(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True
