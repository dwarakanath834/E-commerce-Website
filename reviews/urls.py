from django.urls import path

from . import views

urlpatterns = [path("<int:product_id>/create/", views.create_review, name="create_review")]