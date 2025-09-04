# myApp/utils/money.py
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.core.cache import cache
from myApp.models import FxRate

BASE = "USD"
SYMBOLS = {"USD": "$", "PHP": "₱", "JOD": "JD", "AED": "د.إ", "EUR": "€", "GBP": "£"}
# Minor units (ISO 4217)
MINOR_UNITS = {"USD": 2, "PHP": 2, "EUR": 2, "GBP": 2, "AED": 2, "JOD": 3}

def _to_decimal(x) -> Decimal:
    if x is None: return Decimal("0")
    if isinstance(x, Decimal): return x
    try: return Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError): return Decimal("0")

def _quantize(amount: Decimal, ccy: str) -> Decimal:
    digits = MINOR_UNITS.get((ccy or BASE).upper(), 2)
    step = Decimal(1).scaleb(-digits)  # 10**-digits
    return amount.quantize(step, rounding=ROUND_HALF_UP)

def _rate(to_ccy: str) -> Decimal | None:
    to_ccy = (to_ccy or BASE).upper()
    if to_ccy == BASE:
        return Decimal("1")
    key = f"fx:{BASE}->{to_ccy}"
    cached = cache.get(key)
    if cached is not None:
        return Decimal(str(cached))
    row = FxRate.objects.only("rate").filter(base=BASE, quote=to_ccy).first()
    if not row:
        return None
    cache.set(key, str(row.rate), 60 * 10)  # cache 10 min
    return Decimal(str(row.rate))

def convert(amount_base, to_ccy: str) -> Decimal:
    """Convert from BASE to `to_ccy`; if rate missing, return unconverted amount (rounded for display)."""
    to_ccy = (to_ccy or BASE).upper()
    amt = _to_decimal(amount_base)
    r = _rate(to_ccy)
    if r is None:
        return _quantize(amt, to_ccy)  # symbol will change, amount stays base
    return _quantize(amt * r, to_ccy)

def _format_signed(sym: str, amt: Decimal) -> str:
    # Show minus before symbol: -$12.34
    if amt.is_signed():
        return f"-{sym}{abs(amt):,}"
    return f"{sym}{amt:,}"

def format_money(amount_base, ccy: str) -> str:
    """Format with symbol + thousands + correct decimals (no request needed)."""
    ccy = (ccy or BASE).upper()
    sym = SYMBOLS.get(ccy, f"{ccy} ")
    return _format_signed(sym, convert(amount_base, ccy))

def currency_from_request(request) -> str:
    """Request.currency → session → cookie → BASE."""
    if not request:
        return BASE
    c = getattr(request, "currency", None)
    if c: return c
    try:
        c = request.session.get("currency")
        if c: return c
    except Exception:
        pass
    try:
        c = request.COOKIES.get("currency")
        if c: return c
    except Exception:
        pass
    return BASE

def format_money_from_request(amount_base, request) -> str:
    return format_money(amount_base, currency_from_request(request))
