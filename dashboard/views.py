from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Category, Product
from orders.forms import OrderStatusForm
from orders.models import Order
from reviews.models import Review


@staff_member_required
def overview(request):
    revenue = Order.objects.exclude(status=Order.Status.CANCELLED).aggregate(total=Sum("total"))["total"] or 0
    context = {
        "customer_count": get_user_model().objects.filter(is_staff=False).count(),
        "product_count": Product.objects.count(),
        "order_count": Order.objects.count(),
        "revenue": revenue,
        "recent_orders": Order.objects.select_related("user").prefetch_related("items")[:8],
        "low_stock": Product.objects.filter(stock__lte=5).select_related("category").order_by("stock")[:6],
        "category_count": Category.objects.count(),
        "review_count": Review.objects.count(),
    }
    return render(request, "dashboard/overview.html", context)


@staff_member_required
@require_POST
def update_order_status(request, number):
    form = OrderStatusForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Choose a valid order status.")
        return redirect("dashboard")
    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), number=number)
        new_status = form.cleaned_data["status"]
        if new_status == Order.Status.CANCELLED and order.status != Order.Status.CANCELLED:
            if order.status in [Order.Status.SHIPPED, Order.Status.DELIVERED]:
                messages.error(request, "Shipped or delivered orders cannot be cancelled here.")
                return redirect("dashboard")
            for item in order.items.select_related("product"):
                if item.product_id:
                    product = Product.objects.select_for_update().get(pk=item.product_id)
                    product.stock += item.quantity
                    product.save(update_fields=["stock", "updated_at"])
        elif order.status == Order.Status.CANCELLED and new_status != Order.Status.CANCELLED:
            messages.error(request, "Cancelled orders cannot be reopened.")
            return redirect("dashboard")
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Order {number} updated.")
    return redirect("dashboard")