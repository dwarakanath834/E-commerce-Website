from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_featured", "updated_at")
    list_filter = ("category", "is_featured")
    search_fields = ("name", "description")
    list_editable = ("price", "stock", "is_featured")
    prepopulated_fields = {"slug": ("name",)}