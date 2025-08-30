# app/admin.py
from django.contrib import admin
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
    list_display = ("name", "price", "is_bundle", "free_delivery", "is_active", "created_at")
    list_filter = ("is_bundle", "free_delivery", "is_active", "created_at")
    search_fields = ("name", "slug", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    readonly_fields = ("created_at",)
    inlines = [ProductComponentInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "unit_price", "quantity", "line_total")
    can_delete = False
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "status", "grand_total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "full_name", "email", "phone")
    inlines = [OrderItemInline]
    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
        "subtotal",
        "shipping_cost",
        "discount_total",
        "grand_total",
    )
    fieldsets = (
        ("Order", {"fields": ("order_number", "status", "created_at", "updated_at")}),
        ("Customer", {"fields": ("full_name", "phone", "email")}),
        ("Shipping Address", {"fields": ("address_line1", "city", "province", "zip_code")}),
        ("Options", {"fields": ("shipping_method", "payment_method", "notes")}),
        ("Totals", {"fields": ("subtotal", "shipping_cost", "discount_total", "grand_total")}),
    )


@admin.register(ProductComponent)
class ProductComponentAdmin(admin.ModelAdmin):
    """
    Optional: direct table view for bundle relations (useful for audits/bulk tweaks).
    """
    list_display = ("parent", "component", "quantity")
    search_fields = ("parent__name", "component__name")
    autocomplete_fields = ("parent", "component")
