from django.contrib import admin
from .models import Category, FoodItem


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "vendor", "created_at", "updated_at")
    search_fields = ("name", "vendor__vendor_name")


class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = (
        "name",
        "vendor",
        "category",
        "price",
        "is_available",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "vendor__vendor_name",
        "category__name",
        "price",
    )
    list_filter = ("is_available",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
