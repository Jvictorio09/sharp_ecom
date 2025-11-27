# app/urls.py
from django.urls import path
from . import views
from . import views, views_dashboard as dash
from django.core.paginator import Paginator
from django.db.models import Q


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




    path("checkout/", views.checkout, name="checkout"),
    path("api/countries/", views.country_list_api, name="country_list_api"),
    path("api/address-schema/<str:code>/", views.address_schema_api, name="address_schema_api"),


    path("thanks/", views.thanks, name="thanks"),

    # Order status
    path("order-status/", views.order_status, name="order_status"),
    path("order/<str:order_number>/", views.order_detail, name="order_detail"),

    # Contact
    path("contact/", views.contact, name="contact"),
    path("contact/thanks/", views.contact_thanks, name="contact_thanks"),

     # Back-office (client-facing) dashboard
    path("dashboard/login/", dash.dashboard_login, name="dashboard_login"),
    path("dashboard/logout/", dash.dashboard_logout, name="dashboard_logout"),

    path("dashboard/", dash.dashboard_home, name="dashboard_home"),
    path("dashboard/orders/", dash.order_list, name="dashboard_order_list"),
    path("dashboard/order/<str:order_number>/", dash.order_detail, name="dashboard_order_detail"),


    # Update/Delete
    path("dashboard/order/update/<str:order_number>/", dash.order_update, name="dashboard_order_update"),
    path("dashboard/order/delete/<str:order_number>/", dash.order_delete, name="dashboard_order_delete"),
    path("dashboard/order/json/<str:order_number>/",  # NEW
         dash.order_summary_json, name="dashboard_order_summary_json"),

    # Dashboard bulk actions
    path(
        "dashboard/orders/bulk-delete/",
        dash.order_bulk_delete,
        name="dashboard_order_bulk_delete",
    ),

    # urls.py
    path("dashboard/orders/export/", dash.order_export, name="order_export"),
    path("blogs/", views.blog_sample, name="blogadag"),

    path("blog/", views.blog_index, name="blog_index"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),

    path("api/subscribe/", views.subscribe_create, name="subscribe_create"),
    
        # ======================
    # Dashboard → Promos
    # ======================
    path("dashboard/promos/",                 dash.promo_list,   name="dashboard_promo_list"),
    path("dashboard/promos/new/",             dash.promo_upsert, name="dashboard_promo_new"),
    path("dashboard/promos/<int:pk>/",        dash.promo_upsert, name="dashboard_promo_edit"),
    path("dashboard/promos/<int:pk>/toggle/", dash.promo_toggle, name="dashboard_promo_toggle"),
    path("dashboard/promos/<int:pk>/delete/", dash.promo_delete, name="dashboard_promo_delete"),
    path("api/promo/apply", views.apply_promo_json, name="promo_apply_json"),

    path("legal/", views.legal, name="legal"),

    path("dashboard/wsl/<str:order_number>/", dash.wasselexpress_preview, name="dashboard_wsl_preview"),


    path("wasselexpress/webhook/", views.wasselexpress_webhook, name="wasselexpress_webhook"),

    path("dashboard/products/", dash.product_list, name="dashboard_product_list"),
    path("dashboard/products/new/", dash.product_upsert, name="dashboard_product_new"),
    path("dashboard/products/<int:pk>/", dash.product_upsert, name="dashboard_product_edit"),
    path("dashboard/products/<int:pk>/delete/", dash.product_delete, name="dashboard_product_delete"),
    path("dashboard/products/<int:pk>/toggle/", dash.product_toggle_active, name="dashboard_product_toggle"),
    path("dashboard/products/<int:pk>/price/", dash.product_update_price, name="dashboard_product_update_price"),
    path("dashboard/products/bulk/", dash.product_bulk_action, name="dashboard_product_bulk"),
    
    # ============================================================================
    # CMS Dashboard URLs - All functionality with new design
    # ============================================================================
    path("dashboard/cms/", dash.cms_dashboard_home, name="cms_dashboard_home"),
    # Products (CMS version)
    path("dashboard/cms/products/", dash.product_list, name="cms_product_list"),
    path("dashboard/cms/products/new/", dash.product_upsert, name="cms_product_new"),
    path("dashboard/cms/products/<int:pk>/", dash.product_upsert, name="cms_product_edit"),
    path("dashboard/cms/products/<int:pk>/delete/", dash.product_delete, name="cms_product_delete"),
    path("dashboard/cms/products/<int:pk>/toggle/", dash.product_toggle_active, name="cms_product_toggle"),
    path("dashboard/cms/products/<int:pk>/price/", dash.product_update_price, name="cms_product_update_price"),
    path("dashboard/cms/products/bulk/", dash.product_bulk_action, name="cms_product_bulk"),
    # Orders (CMS version)
    path("dashboard/cms/orders/", dash.order_list, name="cms_order_list"),
    # Promos (CMS version)
    path("dashboard/cms/promos/", dash.promo_list, name="cms_promo_list"),
    path("dashboard/cms/promos/new/", dash.promo_upsert, name="cms_promo_new"),
    path("dashboard/cms/promos/<int:pk>/", dash.promo_upsert, name="cms_promo_edit"),
    path("dashboard/cms/promos/<int:pk>/toggle/", dash.promo_toggle, name="cms_promo_toggle"),
    path("dashboard/cms/promos/<int:pk>/delete/", dash.promo_delete, name="cms_promo_delete"),
    path("dashboard/cms/upload-image/", dash.upload_image, name="upload_image"),
    path("dashboard/cms/gallery/", dash.gallery, name="gallery"),
    
    # SEO
    path("dashboard/cms/seo/", dash.seo_edit, name="seo_edit"),
    
    # Navigation
    path("dashboard/cms/navigation/", dash.navigation_edit, name="navigation_edit"),
    
    # Hero
    path("dashboard/cms/hero/", dash.hero_edit, name="hero_edit"),
    
    # About
    path("dashboard/cms/about/", dash.about_edit, name="about_edit"),
    
    # Stats
    path("dashboard/cms/stats/", dash.stats_list, name="stats_list"),
    path("dashboard/cms/stats/new/", dash.stat_edit, name="stat_new"),
    path("dashboard/cms/stats/<int:stat_id>/", dash.stat_edit, name="stat_edit"),
    path("dashboard/cms/stats/<int:stat_id>/delete/", dash.stat_delete, name="stat_delete"),
    
    # Services
    path("dashboard/cms/services/", dash.services_list, name="services_list"),
    path("dashboard/cms/services/new/", dash.service_edit, name="service_new"),
    path("dashboard/cms/services/<int:service_id>/", dash.service_edit, name="service_edit"),
    path("dashboard/cms/services/<int:service_id>/delete/", dash.service_delete, name="service_delete"),
    
    # Portfolio
    path("dashboard/cms/portfolio/", dash.portfolio_edit, name="portfolio_edit"),
    path("dashboard/cms/portfolio/projects/", dash.portfolio_projects_list, name="portfolio_projects_list"),
    path("dashboard/cms/portfolio/projects/new/", dash.portfolio_project_edit, name="portfolio_project_new"),
    path("dashboard/cms/portfolio/projects/<int:project_id>/", dash.portfolio_project_edit, name="portfolio_project_edit"),
    path("dashboard/cms/portfolio/projects/<int:project_id>/delete/", dash.portfolio_project_delete, name="portfolio_project_delete"),
    
    # Testimonials
    path("dashboard/cms/testimonials/", dash.testimonials_list, name="testimonials_list"),
    path("dashboard/cms/testimonials/new/", dash.testimonial_edit, name="testimonial_new"),
    path("dashboard/cms/testimonials/<int:testimonial_id>/", dash.testimonial_edit, name="testimonial_edit"),
    path("dashboard/cms/testimonials/<int:testimonial_id>/delete/", dash.testimonial_delete, name="testimonial_delete"),
    
    # FAQs
    path("dashboard/cms/faq/", dash.faq_section_edit, name="faq_section_edit"),
    path("dashboard/cms/faqs/", dash.faqs_list, name="faqs_list"),
    path("dashboard/cms/faqs/new/", dash.faq_edit, name="faq_new"),
    path("dashboard/cms/faqs/<int:faq_id>/", dash.faq_edit, name="faq_edit"),
    path("dashboard/cms/faqs/<int:faq_id>/delete/", dash.faq_delete, name="faq_delete"),
    
    # Contact
    path("dashboard/cms/contact/", dash.contact_edit, name="contact_edit"),
    path("dashboard/cms/contact/info/", dash.contact_info_list, name="contact_info_list"),
    path("dashboard/cms/contact/info/new/", dash.contact_info_edit, name="contact_info_new"),
    path("dashboard/cms/contact/info/<int:info_id>/", dash.contact_info_edit, name="contact_info_edit"),
    path("dashboard/cms/contact/info/<int:info_id>/delete/", dash.contact_info_delete, name="contact_info_delete"),
    path("dashboard/cms/contact/fields/", dash.contact_form_fields_list, name="contact_form_fields_list"),
    path("dashboard/cms/contact/fields/new/", dash.contact_form_field_edit, name="contact_form_field_new"),
    path("dashboard/cms/contact/fields/<int:field_id>/", dash.contact_form_field_edit, name="contact_form_field_edit"),
    path("dashboard/cms/contact/fields/<int:field_id>/delete/", dash.contact_form_field_delete, name="contact_form_field_delete"),
    
    # Social Links
    path("dashboard/cms/social/", dash.social_links_list, name="social_links_list"),
    path("dashboard/cms/social/new/", dash.social_link_edit, name="social_link_new"),
    path("dashboard/cms/social/<int:link_id>/", dash.social_link_edit, name="social_link_edit"),
    path("dashboard/cms/social/<int:link_id>/delete/", dash.social_link_delete, name="social_link_delete"),
    
    # Footer
    path("dashboard/cms/footer/", dash.footer_edit, name="footer_edit"),
]
