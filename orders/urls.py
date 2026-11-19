from django.urls import path

from . import views

urlpatterns = [
	path("", views.order_list, name="order_list"),
	path("checkout/", views.checkout, name="checkout"),
	path("<str:number>/", views.order_detail, name="order_detail"),
	path("<str:number>/cancel/", views.cancel_order, name="cancel_order"),
]