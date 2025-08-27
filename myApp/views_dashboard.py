# myApp/views_dashboard.py
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Order

ORDER_STATUSES = [key for key, _ in Order.STATUS_CHOICES]
DASH_AUTH_SESSION_KEY = "dashboard_authed"

# ---- Guard: allow either Django auth OR session flag ----
def dashboard_required(viewfunc):
    @wraps(viewfunc)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get(DASH_AUTH_SESSION_KEY):
            return viewfunc(request, *args, **kwargs)
        next_url = request.get_full_path()
        return redirect(f"/dashboard/login/?next={next_url}")
    return _wrapped

def dashboard_login(request):
    """
    Accepts either:
      1) Django auth (username + password),
      2) Shared gate password via DASHBOARD_PASSWORD (enter in the password field, leave username blank).
    """
    pwd_setting = getattr(settings, "DASHBOARD_PASSWORD", "changeme")
    context = {"next": request.GET.get("next", "/dashboard/")}

    if request.method == "POST":
        next_url = request.POST.get("next") or "/dashboard/"
        username = (request.POST.get("username") or "").strip()
        password = (request.POST.get("password") or "").strip()

        # Try Django auth first if username provided
        if username:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                dj_login(request, user)
                messages.success(request, f"Welcome back, {user.get_username()}.")
                return redirect(next_url)
            messages.error(request, "Invalid username or password.")
            return render(request, "dashboard/login.html", context, status=200)

        # Fallback: shared dashboard password (no username)
        if password == pwd_setting:
            request.session[DASH_AUTH_SESSION_KEY] = True
            messages.success(request, "Welcome back.")
            return redirect(next_url)

        messages.error(request, "Incorrect password.")
        return render(request, "dashboard/login.html", context, status=200)

    return render(request, "dashboard/login.html", context)

def dashboard_logout(request):
    # clear both auth modes
    request.session.pop(DASH_AUTH_SESSION_KEY, None)
    dj_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("/dashboard/login/")

@dashboard_required
def dashboard_home(request):
    kpi = {
        "pending": Order.objects.filter(status="pending").count(),
        "today": Order.objects.filter(created_at__date=timezone.localdate()).count(),
        "sales_30": Order.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).aggregate(total=Sum("grand_total"))["total"] or 0,
    }
    recent = Order.objects.order_by("-created_at")[:10]
    return render(request, "dashboard/home.html", {
        "kpi": kpi,
        "recent": recent,
        "order_statuses": ORDER_STATUSES,
    })

@dashboard_required
def order_list(request):
    status = request.GET.get("status", "all")
    q = (request.GET.get("q") or "").strip()

    qs = Order.objects.all().order_by("-created_at")
    if status != "all":
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(
            Q(order_number__icontains=q) |
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    return render(request, "dashboard/orders.html", {
        "orders": qs[:200],
        "status": status,
        "q": q,
        "order_statuses": ORDER_STATUSES,
    })

@dashboard_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "dashboard/order_detail.html", {"order": order})

# myApp/views_dashboard.py
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@dashboard_required
@require_POST
def order_update(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    new_status = request.POST.get("status", order.status)
    new_tracking = (request.POST.get("tracking") or "").strip()
    new_notes = (request.POST.get("notes") or "").strip()
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/dashboard/"

    # Validate status
    valid_statuses = dict(Order.STATUS_CHOICES).keys()
    if new_status not in valid_statuses:
        messages.error(request, "Invalid status.")
        return redirect(next_url)

    # Track changes
    status_changed = (order.status != new_status)
    tracking_changed = (getattr(order, "tracking_number", "") or "") != new_tracking
    notes_changed = (order.notes or "") != new_notes

    # Apply changes
    order.status = new_status
    if hasattr(order, "tracking_number"):
        order.tracking_number = new_tracking
    order.notes = new_notes

    if status_changed or tracking_changed or notes_changed:
        order.save()
        messages.success(request, f"Order {order.order_number} updated.")

        # Notify the customer if we have their email
        if order.email and (status_changed or tracking_changed):
            _email_order_status_update(request, order, status_changed=status_changed, tracking_changed=tracking_changed)
    else:
        messages.info(request, "No changes made.")

    return redirect(next_url)

def _email_order_status_update(request, order, status_changed=True, tracking_changed=False):
    """
    Sends an email to the customer about the status update (and tracking, if changed).
    Uses HTML + plaintext fallback.
    """
    try:
        if not order.email:
            return

        context = {
            "order": order,
            "request": request,
            "status_changed": status_changed,
            "tracking_changed": tracking_changed,
        }

        # Subject example: "Update: Your SHARP Order SH-123456 is now Shipped"
        status_label = order.get_status_display() if hasattr(order, "get_status_display") else order.status.title()
        subject = f"Update: Your SHARP Order {order.order_number} is now {status_label}"

        text_body = render_to_string("emails/order_status_update.txt", context)
        html_body = render_to_string("emails/order_status_update.html", context)

        send_mail(
            subject=subject,
            message=text_body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[order.email],
            html_message=html_body,
            fail_silently=False,
        )
    except Exception as e:
        # Don't blow up the dashboard on email hiccups; you can log if desired.
        # import logging; logging.getLogger(__name__).exception("Status email failed")
        pass


@dashboard_required
@require_POST
def order_delete(request, order_number):
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/dashboard/"
    get_object_or_404(Order, order_number=order_number).delete()
    messages.info(request, f"Order {order_number} deleted.")
    return redirect(next_url)
