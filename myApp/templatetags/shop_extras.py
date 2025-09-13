# myApp/templatetags/shop_extras.py
from django import template
import re

register = template.Library()

@register.filter
def smart_name(name):
    """
    Replace '+' with '&' and collapse spaces. Safe for None.
    """
    if not isinstance(name, str):
        return name or ""
    # convert "A + B" or "A+B" to "A & B"
    name = re.sub(r"\s*\+\s*", " & ", name)
    # collapse any doubles
    return re.sub(r"\s{2,}", " ", name).strip()

@register.simple_tag
def components_preview(links, limit=3):
    """
    Render a short 'What’s inside' preview:
    '1× Conditioner · 1× Treatment Oil · 1× Sea Salt…'
    Works with QuerySet, list, or manager. Never raises.
    """
    try:
        items_all = list(links)  # forces evaluation if QuerySet/manager
    except Exception:
        items_all = []

    # slice for preview
    head = items_all[: int(limit) if str(limit).isdigit() else 3]

    parts = []
    for link in head:
        try:
            qty = getattr(link, "quantity", 1) or 1
            comp = getattr(link, "component", None)
            comp_name = (getattr(comp, "name", "") or "").strip()
            if comp_name:
                parts.append(f"{qty}× {comp_name}")
        except Exception:
            # skip any bad row instead of crashing the template
            continue

    trailer = "…" if len(items_all) > len(head) else ""
    return (" · ".join(parts) + trailer).strip()
