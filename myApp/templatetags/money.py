# myApp/templatetags/money.py
from django import template
from django.conf import settings
from myApp.utils.money import (
    format_money_from_request_any,  # <-- use this
    format_money_any,               # optional
)

register = template.Library()
PRICE_SRC = getattr(settings, "PRICE_SOURCE_CURRENCY", "USD")

@register.filter(name="money")
def money_filter(amount, request):
    # {{ amount|money:request }} assumes amount is stored in PRICE_SOURCE_CURRENCY (JOD)
    return format_money_from_request_any(amount, PRICE_SRC, request)

@register.filter(name="money_ccy")
def money_ccy_filter(amount, to_ccy):
    # Explicit target currency, still using PRICE_SOURCE_CURRENCY as source
    return format_money_any(amount, PRICE_SRC, (to_ccy or "USD").upper())

@register.simple_tag(takes_context=True, name="money_from")
def money_from_tag(context, amount, from_ccy):
    # When a specific value is NOT in JOD
    req = context.get("request")
    return format_money_from_request_any(amount, from_ccy, req)
