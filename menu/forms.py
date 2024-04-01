from django import forms
from accounts.validators import allow_only_images_validator
from menu.models import Category, FoodItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }


class FoodItemForm(forms.ModelForm):
    image = forms.FileField(
        widget=forms.FileInput(attrs={"class": "btn btn-info w-100"}),
        validators=[allow_only_images_validator],
    )

    class Meta:
        model = FoodItem
        fields = ["category", "name", "description", "price", "image", "is_available"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }
