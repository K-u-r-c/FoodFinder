from django.urls import path

from accounts import views as account_views
from . import views

urlpatterns = [
    path("", account_views.custDashboard, name="customer"),
    path("profile/", views.cprofile, name="cprofile"),
    path("my_orders/", views.my_orders, name="customer_my_orders"),
    path("order_details/<int:order_number>/", views.order_details, name="order_details"),
]
