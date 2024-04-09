from django.contrib import admin
from marketplace.models import Cart


class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "food_item", "quantity", "date_added", "modified_at"]
    search_fields = ["user__username", "food_item__name"]
    list_filter = ["date_added", "modified_at"]


admin.site.register(Cart)
