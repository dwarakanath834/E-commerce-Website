from django.urls import path

from . import views

urlpatterns = [
	path("", views.overview, name="dashboard"),
	path("orders/<str:number>/status/", views.update_order_status, name="update_order_status"),
]