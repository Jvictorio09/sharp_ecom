# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Catalog
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),

    # Cart
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),  # NEW
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/summary.json", views.cart_summary_json, name="cart_summary_json"),

    # Checkout
    path("checkout/", views.checkout, name="checkout"),
    path("thanks/", views.thanks, name="thanks"),

    # Order status
    path("order-status/", views.order_status, name="order_status"),
    path("order/<str:order_number>/", views.order_detail, name="order_detail"),

    # Contact
    path("contact/", views.contact, name="contact"),
    path("contact/thanks/", views.contact_thanks, name="contact_thanks"),
]
