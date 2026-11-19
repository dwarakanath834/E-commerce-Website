from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from urllib.parse import urlencode
from django.views.decorators.http import require_POST

from catalog.models import Product

from .models import Cart, CartItem


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product", "product__category")
    return render(request, "cart/cart.html", {"cart": cart, "items": items})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 0
    if quantity < 1:
        messages.error(request, "Choose a valid quantity.")
    elif quantity > product.stock:
        messages.error(request, f"Only {product.stock} left in stock.")
    elif not request.user.is_authenticated:
        request.session["pending_cart_item"] = {"product_id": product.pk, "quantity": quantity}
        messages.info(request, "Sign in or create an account to add this find to your bag.")
        login_url = f"{reverse('login')}?{urlencode({'next': reverse('resume_pending_cart')})}"
        return redirect(login_url)
    else:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
        if not created:
            if item.quantity + quantity > product.stock:
                messages.error(request, f"Only {product.stock} left in stock.")
            else:
                item.quantity += quantity
                item.save(update_fields=["quantity"])
                messages.success(request, "Cart updated.")
        else:
            messages.success(request, "Added to your cart.")
    return redirect(request.POST.get("next") or "cart_detail")


@login_required
def resume_pending_cart(request):
    pending = request.session.pop("pending_cart_item", None)
    if not isinstance(pending, dict):
        return redirect("cart_detail")
    try:
        product = Product.objects.get(pk=int(pending["product_id"]))
        quantity = int(pending["quantity"])
    except (Product.DoesNotExist, KeyError, TypeError, ValueError):
        messages.error(request, "That item is no longer available.")
        return redirect("product_list")
    if quantity < 1 or quantity > product.stock:
        messages.error(request, f"Only {product.stock} of {product.name} are available.")
        return redirect("product_detail", slug=product.slug)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
    if not created:
        if item.quantity + quantity > product.stock:
            messages.error(request, f"Only {product.stock} of {product.name} are available.")
            return redirect("product_detail", slug=product.slug)
        item.quantity += quantity
        item.save(update_fields=["quantity"])
    messages.success(request, "Added to your bag.")
    return redirect("cart_detail")


@login_required
@require_POST
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem.objects.select_related("product"), pk=item_id, cart__user=request.user)
    try:
        quantity = int(request.POST.get("quantity", 0))
    except (TypeError, ValueError):
        quantity = 0
    if quantity <= 0:
        item.delete()
        messages.info(request, "Item removed from your cart.")
    elif quantity > item.product.stock:
        messages.error(request, f"Only {item.product.stock} left in stock.")
    else:
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        messages.success(request, "Cart updated.")
    return redirect("cart_detail")


@login_required
@require_POST
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, "Item removed from your cart.")
    return redirect("cart_detail")