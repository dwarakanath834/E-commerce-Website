from django.urls import path

from . import views

urlpatterns = [
	path("", views.cart_detail, name="cart_detail"),
	path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
	path("resume-pending/", views.resume_pending_cart, name="resume_pending_cart"),
	path("item/<int:item_id>/update/", views.update_cart_item, name="update_cart_item"),
	path("item/<int:item_id>/remove/", views.remove_cart_item, name="remove_cart_item"),
]