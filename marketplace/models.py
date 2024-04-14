from django.db import models

from accounts.models import User
from menu.models import FoodItem


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "food_item")

    def __unicode__(self):
        return self.user

    def get_total(self):
        return self.food_item.price * self.quantity


class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Tax Percentage (%)')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Taxes"

    def __str__(self):
        return self.tax_type
