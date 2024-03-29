from django.shortcuts import get_object_or_404, redirect, render
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.forms import CategoryForm
from menu.models import Category, FoodItem
from vendor.forms import VendorForm
from vendor.models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("vendorProfile")
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
            messages.error(request, "Error Updating Profile")
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        "profile_form": profile_form,
        "vendor_form": vendor_form,
        "vendor": vendor,
        "profile": profile,
    }

    return render(request, "vendor/vendorProfile.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def menuBuilder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(vendor=vendor).order_by("created_at")
    context = {"categories": categories}
    return render(request, "vendor/menuBuilder.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def foodItems_by_category(request, pk):
    vendor = Vendor.objects.get(user=request.user)
    category = get_object_or_404(Category, pk=pk)
    foodItems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {"foodItems": foodItems, "category": category}
    return render(request, "vendor/foodItems_by_category.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def addCategory(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            categoryName = form.cleaned_data["name"]
            category = form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category.slug = slugify(categoryName)
            form.save()
            messages.success(request, "Category Added Successfully")
            return redirect("menuBuilder")
        else:
            print(form.errors)
            messages.error(request, "Error Adding Category")
    else:
        form = CategoryForm()

    context = {"form": form}
    return render(request, "vendor/addCategory.html", context)


def editCategory(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            categoryName = form.cleaned_data["name"]
            category = form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category.slug = slugify(categoryName)
            form.save()
            messages.success(request, "Category Updated Successfully")
            return redirect("menuBuilder")
        else:
            print(form.errors)
            messages.error(request, "Error Adding Category")
    else:
        form = CategoryForm(instance=category)

    context = {"form": form, "category": category}
    return render(request, "vendor/editCategory.html", context)


def deleteCategory(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category Deleted Successfully")
    return redirect("menuBuilder")
