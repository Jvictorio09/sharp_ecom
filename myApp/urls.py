from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),

    # cart
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/summary.json", views.cart_summary_json, name="cart_summary_json"),

    path("checkout/", views.checkout, name="checkout"),
    path("thanks/", views.thanks, name="thanks"),

    path("contact/", views.contact, name="contact"),
]
