from django.shortcuts import redirect, render
from vendor.forms import VendorForm
from .models import User, UserProfile
from .forms import UserForm
from django.contrib import messages


def registerUser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "User registered successfully")
            return redirect("registerUser")
        else:
            messages.error(request, "User registration failed")
    else:
        form = UserForm()

    context = {"form": form}
    return render(request, "accounts/registerUser.html", context)


def registerVendor(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and vendor_form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.RESTAURANT
            user.save()

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()

            messages.success(
                request,
                "Your account has been registered succesfully, please wait for the approval.",
            )
            return redirect("registerVendor")
        else:
            messages.error(request, "Vendor registration failed")
    else:
        form = UserForm()
        vendor_form = VendorForm()

    context = {"form": form, "vendor_form": vendor_form}
    return render(request, "accounts/registerVendor.html", context)
