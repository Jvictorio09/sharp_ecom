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
