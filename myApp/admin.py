# app/admin.py
from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug", "short_description")
    prepopulated_fields = {"slug": ("name",)}  # helpful when adding; save() still enforces uniqueness
    ordering = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "unit_price", "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "created_at", "status", "grand_total")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "full_name", "email", "phone")
    inlines = [OrderItemInline]
    readonly_fields = ("order_number", "created_at", "updated_at", "subtotal", "shipping_cost",
                       "discount_total", "grand_total")
    fieldsets = (
        ("Order", {
            "fields": ("order_number", "status", "created_at", "updated_at")
        }),
        ("Customer", {
            "fields": ("full_name", "phone", "email")
        }),
        ("Shipping Address", {
            "fields": ("address_line1", "city", "province", "zip_code")
        }),
        ("Options", {
            "fields": ("shipping_method", "payment_method", "notes")
        }),
        ("Totals", {
            "fields": ("subtotal", "shipping_cost", "discount_total", "grand_total")
        }),
    )
