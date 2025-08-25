from django.contrib import admin
from .models import Product, Cart, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Cart)
admin.site.register(CartItem)
