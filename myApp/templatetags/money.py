# myApp/templatetags/money.py
from django import template
from myApp.utils.money import (
    format_money, format_money_from_request, currency_from_request
)

register = template.Library()

@register.filter(name="money")
def money_filter(amount_base, request):
    """Usage: {{ amount|money:request }}"""
    return format_money_from_request(amount_base, request)

@register.filter(name="money_ccy")
def money_ccy_filter(amount_base, ccy):
    """Usage: {{ amount|money_ccy:'PHP' }}"""
    return format_money(amount_base, ccy)

@register.simple_tag(takes_context=True, name="money_tag")
def money_tag(context, amount_base):
    req = context.get("request")
    return format_money_from_request(amount_base, req)
