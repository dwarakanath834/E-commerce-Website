from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("number", "user__username", "email")
    readonly_fields = ("status",)
    inlines = [OrderItemInline]

    def has_delete_permission(self, request, obj=None):
        return False