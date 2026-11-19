import uuid
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Address
from cartapp.models import Cart
from catalog.models import Product

from .forms import CheckoutForm
from .models import Order, OrderItem


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = list(cart.items.select_related("product"))
    if not cart_items:
        messages.info(request, "Your cart is waiting for something good.")
        return redirect("product_list")
    initial = {"full_name": request.user.get_full_name(), "email": request.user.email}
    address = request.user.addresses.first()
    if address:
        initial.update({key: getattr(address, key) for key in ("full_name", "email", "phone", "street", "city", "state", "postal_code")})
    else:
        initial["phone"] = request.user.profile.phone
    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                locked_items = list(cart.items.select_for_update().select_related("product"))
                if not locked_items:
                    messages.error(request, "Your cart is empty.")
                    return redirect("cart_detail")
                checked_items = []
                subtotal = Decimal("0.00")
                for item in locked_items:
                    product = Product.objects.select_for_update().get(pk=item.product_id)
                    if item.quantity > product.stock:
                        raise ValueError(f"Only {product.stock} of {product.name} are available.")
                    subtotal += product.price * item.quantity
                    checked_items.append((item, product))
                order = Order.objects.create(
                    user=request.user,
                    number=f"SE{uuid.uuid4().hex[:10].upper()}",
                    payment_method=form.cleaned_data["payment_method"],
                    subtotal=subtotal,
                    shipping=Decimal("0.00"),
                    total=subtotal,
                    **{key: form.cleaned_data[key] for key in ("full_name", "email", "phone", "street", "city", "state", "postal_code")},
                )
                for item, product in checked_items:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=item.quantity,
                    )
                    product.stock -= item.quantity
                    product.save(update_fields=["stock", "updated_at"])
                cart.items.all().delete()
                if form.cleaned_data["save_address"]:
                    Address.objects.filter(user=request.user).update(is_default=False)
                    Address.objects.create(user=request.user, is_default=True, **{
                        key: form.cleaned_data[key] for key in ("full_name", "email", "phone", "street", "city", "state", "postal_code")
                    })
        except ValueError as error:
            form.add_error(None, str(error))
        else:
            messages.success(request, f"Order {order.number} is confirmed. This is a demo payment.")
            return redirect("order_detail", number=order.number)
    return render(request, "orders/checkout.html", {"form": form, "items": cart_items, "subtotal": sum((i.line_total for i in cart_items), Decimal("0.00"))})


@login_required
def order_list(request):
    orders = request.user.orders.prefetch_related("items").all()
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), number=number, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
@require_POST
def cancel_order(request, number):
    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), number=number, user=request.user)
        if order.status != Order.Status.PENDING:
            messages.error(request, "Only pending orders can be cancelled.")
            return redirect("order_detail", number=number)
        for item in order.items.select_related("product"):
            if item.product_id:
                product = Product.objects.select_for_update().get(pk=item.product_id)
                product.stock += item.quantity
                product.save(update_fields=["stock", "updated_at"])
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
    messages.success(request, "Your order has been cancelled and stock has been restored.")
    return redirect("order_detail", number=number)