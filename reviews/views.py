from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from catalog.models import Product
from orders.models import Order

from .forms import ReviewForm


@login_required
@require_POST
def create_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    has_purchased = Order.objects.filter(
        user=request.user,
        status__in=[Order.Status.CONFIRMED, Order.Status.PROCESSING, Order.Status.SHIPPED, Order.Status.DELIVERED],
        items__product=product,
    ).exists()
    if not has_purchased:
        messages.error(request, "Reviews are available after purchasing this item.")
    elif product.reviews.filter(user=request.user).exists():
        messages.error(request, "You have already reviewed this item.")
    else:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thanks for sharing your review.")
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    return redirect("product_detail", slug=product.slug)