from django.urls import path

from accounts import views as account_views
from . import views

urlpatterns = [
    path("", account_views.custDashboard, name="customer"),
    path("profile/", views.cprofile, name="cprofile"),
]
