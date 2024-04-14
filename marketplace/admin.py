from django.contrib import admin

from marketplace.models import Cart, Tax


class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "food_item", "quantity", "date_added", "modified_at"]
    search_fields = ["user__username", "food_item__name"]
    list_filter = ["date_added", "modified_at"]


class TaxAdmin(admin.ModelAdmin):
    list_display = ["tax_type", "tax_percentage", "is_active"]
    search_fields = ["tax_type"]
    list_filter = ["is_active"]


admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)
