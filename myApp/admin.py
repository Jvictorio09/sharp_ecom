from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductComponent, Order, OrderItem

class ProductComponentInline(admin.TabularInline):
    """
    Lets you define bundle contents on a Product marked is_bundle=True.
    """
    model = ProductComponent
    fk_name = "parent"
    extra = 1
    fields = ("component", "quantity")
    autocomplete_fields = ("component",)
    verbose_name = "Bundle item"
    verbose_name_plural = "Bundle contents"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # show a tiny thumbnail in the list
    @admin.display(description="Image")
    def thumb(self, obj: Product):
        # use first gallery image if available, else image_url
        first = (obj.gallery[0] if getattr(obj, "gallery", []) else None) or obj.image_url
        if not first:
            return "—"
        return format_html(
            '<img src="{}" style="height:38px;width:38px;object-fit:cover;border-radius:6px;border:1px solid #eee;" />',
            first
        )

    list_display = ("thumb", "name", "price", "is_bundle", "free_delivery", "is_active", "created_at")
    list_filter = ("is_bundle", "free_delivery", "is_active", "created_at")
    search_fields = ("name", "slug", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    # make gallery_csv easier to paste into (describe “comma-separated or newlines”)
    readonly_fields = ()
    fieldsets = (
        (None, {
            "fields": ("name", "slug", "short_description", "description")
        }),
        ("Media", {
            "fields": ("image_url", "gallery_csv"),
            "description": "Paste image URLs separated by commas OR new lines. First image becomes the default."
        }),
        ("Pricing & Flags", {
            "fields": ("price", "is_bundle", "free_delivery", "is_active")
        }),
    )

    # only show bundle contents inline when the product is a bundle
    inlines = []

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj and getattr(obj, "is_bundle", False):
            inlines.append(ProductComponentInline(self.model, self.admin_site))
        return inlines

    # normalize gallery input: allow newlines, store as CSV
    def save_model(self, request, obj, form, change):
        csv = (obj.gallery_csv or "")
        # replace newlines with commas, collapse multiple commas/spaces
        csv = ",".join([p.strip() for chunk in csv.replace("\r", "").split("\n") for p in chunk.split(",") if p.strip()])
        obj.gallery_csv = csv
        super().save_model(request, obj, form, change)



from django.contrib import admin
from .models import Post, PostBlock

class BlockInline(admin.TabularInline):
    model = PostBlock
    extra = 0
    fields = ("order","kind","level","text","image1","image2","caption","prod_query")

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title","published_at")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [BlockInline]


from django.contrib import admin
from django.utils.html import format_html
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    @admin.display(description="Status")
    def status_badge(self, obj):
        active = obj.unsubscribed_at is None
        if active and obj.is_confirmed:
            color, label = "#0ea5e9", "Active • confirmed"
        elif active:
            color, label = "#22c55e", "Active"
        else:
            color, label = "#ef4444", "Unsubscribed"
        return format_html('<span style="padding:.2em .6em;border-radius:999px;background:{}20;color:{};font-size:12px;">{}</span>', color, color, label)

    list_display = ("email", "name", "status_badge", "source", "created_at")
    list_filter  = ("source", "is_confirmed", "created_at")
    search_fields = ("email", "name", "ua")
    ordering = ("-created_at",)


# --- Orders admin (safe + dynamic) ------------------------------------------
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("name", "quantity", "unit_price", "line_total")
    readonly_fields = ("name", "quantity", "unit_price", "line_total")
    can_delete = False
    show_change_link = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Dynamic, defensive admin that only shows fields your Order model actually has.
    It won’t blow up if optional columns (e.g. promo fields) are missing.
    """

    # ---------- list page ----------
    @admin.display(description="Order #")
    def number(self, obj):
        return getattr(obj, "order_number", obj.pk)

    @admin.display(description="Customer")
    def customer(self, obj):
        return getattr(obj, "full_name", "") or "—"

    @admin.display(description="Contact")
    def contact(self, obj):
        email = getattr(obj, "email", "") or ""
        phone = getattr(obj, "phone", "") or ""
        if email and phone:
            return f"{email}  •  {phone}"
        return email or phone or "—"

    @admin.display(description="Country")
    def country_col(self, obj):
        return getattr(obj, "country", "") or "—"

    @admin.display(description="Total")
    def total_col(self, obj):
        val = getattr(obj, "grand_total", None)
        return f"{val:.2f}" if val is not None else "—"

    @admin.display(description="Status")
    def status_col(self, obj):
        return (getattr(obj, "status", "") or "—").title()

    @admin.display(description="Created")
    def created_col(self, obj):
        return getattr(obj, "created_at", None) or getattr(obj, "created", None)

    list_display = ("number", "customer", "contact", "country_col", "total_col", "status_col", "created_col")
    inlines = [OrderItemInline]

    # ---------- detail page ----------
    @admin.display(description="Ship to")
    def shipping_address_pretty(self, obj):
        txt = getattr(obj, "shipping_address_text", "") or ""
        if txt:
            return format_html('<div style="white-space:pre-line">{}</div>', txt.replace("<", "&lt;").replace(">", "&gt;"))
        data = getattr(obj, "shipping_address", None)
        if isinstance(data, dict) and data:
            # Join non-empty values in a readable order
            values = [str(v).strip() for v in data.values() if str(v).strip()]
            return ", ".join(values) if values else "—"
        return "—"

    def _fieldnames(self):
        # Actual model field names, used for dynamic decisions
        return {f.name for f in self.model._meta.get_fields()}

    def get_readonly_fields(self, request, obj=None):
        names = self._fieldnames()
        ro = {"shipping_address_pretty"}
        # Totals are usually computed/immutable
        for f in ("subtotal", "shipping_cost", "discount_total", "grand_total"):
            if f in names:
                ro.add(f)
        # Don’t allow editing generated order number once created
        if obj and "order_number" in names:
            ro.add("order_number")
        # Timestamps if present
        for f in ("created_at", "updated_at", "created", "updated"):
            if f in names:
                ro.add(f)
        return tuple(ro)

    def get_fieldsets(self, request, obj=None):
        names = self._fieldnames()
        def pick(*candidates):
            return [f for f in candidates if f in names]

        general = pick("order_number", "status", "payment_method", "shipping_method", "promo_code", "promo_label", "tracking_number")
        customer = pick("full_name", "email", "phone", "country")
        totals   = pick("subtotal", "shipping_cost", "discount_total", "grand_total")
        meta     = pick("created_at", "updated_at", "created", "updated")

        fieldsets = []
        if general or "shipping_address_pretty" or "notes" in names:
            block = {
                "fields": tuple(general + (["shipping_address_pretty"] if True else []) + pick("notes"))
            }
            fieldsets.append(("Order", block))
        if customer:
            fieldsets.append(("Customer", {"fields": tuple(customer)}))
        if totals:
            fieldsets.append(("Totals", {"fields": tuple(totals)}))
        if meta:
            fieldsets.append(("Meta", {"fields": tuple(meta)}))
        return fieldsets

    # Search / filters / ordering made dynamic so we don’t reference missing fields
    def get_search_fields(self, request):
        names = self._fieldnames()
        return tuple(f for f in ("order_number", "full_name", "email", "phone") if f in names)

    def get_list_filter(self, request):
        names = self._fieldnames()
        return tuple(f for f in ("status", "payment_method", "shipping_method", "country", "created_at") if f in names)

    def get_ordering(self, request):
        names = self._fieldnames()
        if "created_at" in names:
            return ("-created_at",)
        return ("-id",)
