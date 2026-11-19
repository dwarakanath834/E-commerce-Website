def cart_count(request):
    if request.user.is_authenticated:
        from django.db.models import Sum

        from .models import Cart

        cart = Cart.objects.filter(user=request.user).first()
        count = cart.items.aggregate(total=Sum("quantity"))["total"] if cart else 0
        return {"cart_count": count or 0}
    return {"cart_count": 0}