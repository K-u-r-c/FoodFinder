from django.urls import path
from accounts import views as accounts_views
from . import views

urlpatterns = [
    path("", accounts_views.vendorDashboard, name="vendor"),
    path("profile/", views.vendorProfile, name="vendorProfile"),
]
