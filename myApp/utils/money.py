from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.core.cache import cache
from myApp.models import FxRate

BASE = "USD"  # fine; not relied upon for cross rates
SYMBOLS = {"USD": "$", "PHP": "₱", "JOD": "JD", "AED": "د.إ", "EUR": "€", "GBP": "£"}
MINOR_UNITS = {"USD": 2, "PHP": 2, "EUR": 2, "GBP": 2, "AED": 2, "JOD": 3}

def _to_decimal(x) -> Decimal:
    if x is None: return Decimal("0")
    if isinstance(x, Decimal): return x
    try: return Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError): return Decimal("0")

def _quantize(amount: Decimal, ccy: str) -> Decimal:
    digits = MINOR_UNITS.get((ccy or BASE).upper(), 2)
    step = Decimal(1).scaleb(-digits)
    return amount.quantize(step, rounding=ROUND_HALF_UP)

def _pair_rate(base_ccy: str, quote_ccy: str) -> Decimal | None:
    """Return base->quote; if only reverse exists, invert. Cached."""
    b = (base_ccy or BASE).upper()
    q = (quote_ccy or BASE).upper()
    if b == q: return Decimal("1")

    key = f"fx:{b}->{q}"
    cached = cache.get(key)
    if cached is not None:
        try: return Decimal(str(cached))
        except Exception: pass

    # direct
    row = FxRate.objects.only("rate").filter(base=b, quote=q).first()
    if row:
        cache.set(key, str(row.rate), 600)
        return Decimal(str(row.rate))

    # reverse
    row = FxRate.objects.only("rate").filter(base=q, quote=b).first()
    if row:
        inv = Decimal("1") / Decimal(str(row.rate))
        cache.set(key, str(inv), 600)
        return inv

    return None

def rate_between(from_ccy: str, to_ccy: str) -> Decimal | None:
    """Rate f->t. Try direct, invert, else bridge via anchors."""
    f = (from_ccy or BASE).upper()
    t = (to_ccy or BASE).upper()
    if f == t: return Decimal("1")

    r = _pair_rate(f, t)
    if r is not None: return r

    for a in ("USD","JOD","EUR","GBP","AED","PHP"):
        r1 = _pair_rate(f, a)
        r2 = _pair_rate(a, t)
        if r1 is not None and r2 is not None:
            return r1 * r2
    return None

# Backwards-compatible: BASE -> to_ccy
def convert(amount_base, to_ccy: str) -> Decimal:
    return convert_any(amount_base, BASE, to_ccy)

# New: any -> any
def convert_any(amount, from_ccy: str, to_ccy: str) -> Decimal:
    amt = _to_decimal(amount)
    r = rate_between(from_ccy, to_ccy)
    if r is None:
        return _quantize(amt, to_ccy)  # show unconverted but rounded (rare)
    return _quantize(amt * r, to_ccy)

def _format_signed(sym: str, amt: Decimal) -> str:
    return f"-{sym}{abs(amt):,}" if amt.is_signed() else f"{sym}{amt:,}"

def format_money(amount_base, ccy: str) -> str:
    ccy = (ccy or BASE).upper()
    sym = SYMBOLS.get(ccy, f"{ccy} ")
    return _format_signed(sym, convert(amount_base, ccy))

def format_money_any(amount, from_ccy: str, to_ccy: str) -> str:
    to_ccy = (to_ccy or BASE).upper()
    sym = SYMBOLS.get(to_ccy, f"{to_ccy} ")
    conv = convert_any(amount, from_ccy, to_ccy)
    return _format_signed(sym, conv)

def currency_from_request(request) -> str:
    if not request: return BASE
    c = (getattr(request, "currency", None)
         or getattr(getattr(request, "session", None), "get", lambda *_: None)("currency")
         or getattr(getattr(request, "COOKIES", {}), "get", lambda *_: None)("currency"))
    return (c or BASE)

def format_money_from_request(amount_base, request) -> str:
    return format_money(amount_base, currency_from_request(request))

def format_money_from_request_any(amount, from_ccy: str, request) -> str:
    return format_money_any(amount, from_ccy, currency_from_request(request))
