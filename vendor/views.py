from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from vendor.forms import VendorForm, OpeningHourForm
from vendor.models import Vendor, OpeningHour


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


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def editCategory(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            categoryName = form.cleaned_data["name"]
            category = form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category.save()
            category.slug = slugify(categoryName) + "-" + str(category.id)
            category.save()
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


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def deleteCategory(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category Deleted Successfully")
    return redirect("menuBuilder")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def addFood(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodName = form.cleaned_data["name"]
            food = form.save(commit=False)
            food.vendor = Vendor.objects.get(user=request.user)
            food.slug = slugify(foodName)
            form.save()
            messages.success(request, "Food Item Added Successfully")
            return redirect("foodItems_by_category", pk=food.category.pk)
        else:
            print(form.errors)
            messages.error(request, "Error Adding Food Item")
    else:
        form = FoodItemForm()
        form.fields["category"].queryset = Category.objects.filter(
            vendor=Vendor.objects.get(user=request.user)
        )

    context = {"form": form}
    return render(request, "vendor/addFood.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def editFood(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodName = form.cleaned_data["name"]
            food = form.save(commit=False)
            food.vendor = Vendor.objects.get(user=request.user)
            food.slug = slugify(foodName)
            form.save()
            messages.success(request, "Food Item Updated Successfully")
            return redirect("foodItems_by_category", pk=food.category.pk)
        else:
            print(form.errors)
            messages.error(request, "Error Adding Category")
    else:
        form = FoodItemForm(instance=food)
        form.fields["category"].queryset = Category.objects.filter(
            vendor=Vendor.objects.get(user=request.user)
        )

    context = {"form": form, "food": food}
    return render(request, "vendor/editFood.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def deleteFood(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, "Food Deleted Successfully")
    return redirect("foodItems_by_category", pk=food.category.pk)


def openingHours(request):
    opening_hours = OpeningHour.objects.filter(vendor=Vendor.objects.get(user=request.user))
    form = OpeningHourForm()
    context = {"openingHours": opening_hours, "form": form}
    return render(request, "vendor/openingHours.html", context)


def addOpeningHour(request):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest" and request.method == "POST":
            day = request.POST.get("day")
            from_hour = request.POST.get("from_hour")
            to_hour = request.POST.get("to_hour")
            is_closed = request.POST.get("is_closed")
            try:
                opening_hour = OpeningHour.objects.create(
                    vendor=Vendor.objects.get(user=request.user),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed,
                )
                if opening_hour:
                    day = OpeningHour.objects.get(id=opening_hour.id)
                    if day.is_closed:
                        response = {
                            "success": "Opening Hour Added Successfully",
                            "id": opening_hour.id,
                            "day": day.get_day_display(),
                            "is_closed": "True",
                        }
                    else:
                        response = {
                            "success": "Opening Hour Added Successfully",
                            "id": opening_hour.id,
                            "day": day.get_day_display(),
                            "from_hour": day.from_hour,
                            "to_hour": day.to_hour,
                        }
                    return JsonResponse(response)
            except IntegrityError as e:
                return JsonResponse(
                    {"error": from_hour + " - " + to_hour + " already exists for this day !"})
        else:
            return JsonResponse({"error": "Invalid Request"})


def removeOpeningHour(request, pk):
    if request.user.is_authenticated and request.headers.get("x-requested-with") == "XMLHttpRequest":
        opening_hour = get_object_or_404(OpeningHour, pk=pk)
        opening_hour.delete()
        return JsonResponse({"success": "Opening Hour Removed Successfully", "id": pk})
    else:
        return JsonResponse({"error": "Invalid Request"})
