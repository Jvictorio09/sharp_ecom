# myApp/middleware.py
import ipaddress, re
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

SUPPORTED = {"USD", "PHP", "JOD", "AED", "EUR", "GBP"}
COUNTRY_TO_CCY = {"PH":"PHP","JO":"JOD","AE":"AED","US":"USD","GB":"GBP","DE":"EUR"}
DEFAULT_COUNTRY = "US"  # safest global fallback

def _client_ip(request):
    # Works behind proxies/CDNs too
    return (
        request.META.get("HTTP_CF_CONNECTING_IP")                       # Cloudflare (if you have it)
        or (request.META.get("HTTP_X_FORWARDED_FOR") or "").split(",")[0].strip()
        or request.META.get("REMOTE_ADDR", "")
    )

def _is_private(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except Exception:
        return True

def _country_from_accept_language(al: str | None) -> str | None:
    if not al: return None
    for token in al.split(","):
        token = token.split(";")[0].strip()  # e.g., en-PH
        m = re.match(r"^[A-Za-z]{2,3}-(?P<region>[A-Za-z]{2})$", token)
        if m: return m.group("region").upper()
        if token.lower() in ("fil", "tl", "tagalog"): return "PH"
    return None

def _country_from_ip_http(ip: str) -> str | None:
    """
    No-signup IP → country lookup using ipwho.is.
    We cache by IP for 24h; timeouts are tiny so requests never block your app.
    """
    if not ip or _is_private(ip):
        return None
    key = f"ipcc:{ip}"
    cached = cache.get(key)
    if cached: return cached

    try:
        import requests  # pip install requests
        r = requests.get(f"https://ipwho.is/{ip}?fields=country_code", timeout=1.8)
        if r.ok:
            cc = (r.json() or {}).get("country_code")
            if cc:
                cc = cc.upper()
                cache.set(key, cc, 60*60*24)
                return cc
    except Exception:
        pass
    return None

class CurrencyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 0) Manual override still supported (?currency=PHP)
        q = (request.GET.get("currency") or "").upper()
        if q in SUPPORTED:
            request.session["currency"] = q

        # 1) Session
        cur = request.session.get("currency")
        if cur in SUPPORTED:
            request.currency = cur
            return

        # 2) Cookie
        cookie_ccy = (request.COOKIES.get("currency") or "").upper()
        if cookie_ccy in SUPPORTED:
            request.session["currency"] = cookie_ccy
            request.currency = cookie_ccy
            return

        # 3) Cloudflare header if present (no HTTP call needed)
        country = (request.META.get("HTTP_CF_IPCOUNTRY") or "").upper()

        # 4) Otherwise, look up by IP (cached)
        if not country:
            ip = _client_ip(request)
            country = _country_from_ip_http(ip) or ""

        # 5) Fall back to Accept-Language (en-PH / fil / tl)
        if not country:
            country = _country_from_accept_language(request.META.get("HTTP_ACCEPT_LANGUAGE")) or ""

        # 6) Dev default so localhost “just works”
        if not country and request.get_host().startswith(("127.0.0.1", "localhost")):
            from django.conf import settings
            country = "PH" if getattr(settings, "DEBUG", False) else DEFAULT_COUNTRY

        # Finalize
        country = (country or DEFAULT_COUNTRY).upper()
        request.currency = COUNTRY_TO_CCY.get(country, "USD")
        request.session["currency"] = request.currency

    def process_response(self, request, response):
        ccy = getattr(request, "currency", None)
        if ccy in SUPPORTED:
            response.set_cookie("currency", ccy, max_age=60*60*24*365, samesite="Lax")
        return response