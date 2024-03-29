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
]
