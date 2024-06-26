from django.urls import path

from accounts import views as accounts_views
from . import views

urlpatterns = [
    path("", accounts_views.vendorDashboard, name="vendor"),
    path("profile/", views.vendorProfile, name="vendorProfile"),
    path("menuBuilder/", views.menuBuilder, name="menuBuilder"),
    path(
        "menuBuilder/category/<int:pk>",
        views.foodItems_by_category,
        name="foodItems_by_category",
    ),
    path("menuBuilder/category/add", views.addCategory, name="addCategory"),
    path("menuBuilder/category/edit/<int:pk>", views.editCategory, name="editCategory"),
    path(
        "menuBuilder/category/delete/<int:pk>",
        views.deleteCategory,
        name="deleteCategory",
    ),
    path("menuBuilder/food/add", views.addFood, name="addFood"),
    path("menuBuilder/food/edit/<int:pk>", views.editFood, name="editFood"),
    path("menuBuilder/food/delete/<int:pk>", views.deleteFood, name="deleteFood"),
    path("openingHours/", views.openingHours, name="openingHours"),
    path("openingHours/add/", views.addOpeningHour, name="addOpeningHour"),
    path("openingHours/remove/<int:pk>", views.removeOpeningHour, name="removeOpeningHour"),
    path("order_details/<str:order_number>", views.order_details, name="vendor_order_details"),
    path("my_orders/", views.my_orders, name="vendor_my_orders"),
]
