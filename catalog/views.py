from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def home(request):
    products = Product.objects.select_related("category")
    context = {
        "categories": Category.objects.all(),
        "featured_products": products.filter(is_featured=True, stock__gt=0)[:4],
        "latest_products": products.filter(stock__gt=0)[:8],
        "popular_products": products.filter(stock__gt=0).annotate(
            units_sold=Sum("order_items__quantity", filter=~Q(order_items__order__status="cancelled"))
        ).order_by("-units_sold", "-created_at")[:4],
    }
    return render(request, "home.html", context)


def product_list(request):
    products = Product.objects.select_related("category").filter(stock__gt=0)
    search = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    sort = request.GET.get("sort", "newest")
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if category:
        products = products.filter(category__slug=category)
    sort_fields = {"price-low": "price", "price-high": "-price", "name": "name", "newest": "-created_at"}
    products = products.order_by(sort_fields.get(sort, "-created_at"))
    page = Paginator(products, 12).get_page(request.GET.get("page"))
    return render(request, "catalog/products.html", {
        "page": page,
        "products": page.object_list,
        "categories": Category.objects.all(),
        "search": search,
        "selected_category": category,
        "sort": sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    reviews = product.reviews.select_related("user")
    has_purchased = request.user.is_authenticated and product.order_items.filter(
        order__user=request.user, order__status__in=["confirmed", "processing", "shipped", "delivered"]
    ).exists()
    already_reviewed = request.user.is_authenticated and product.reviews.filter(user=request.user).exists()
    recommendations = Product.objects.filter(category=product.category, stock__gt=0).exclude(pk=product.pk)[:4]
    return render(request, "catalog/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "has_purchased": has_purchased,
        "already_reviewed": already_reviewed,
        "recommendations": recommendations,
    })