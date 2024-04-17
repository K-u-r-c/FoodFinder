import datetime

from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode

from accounts.utils import (
    detect_user,
    send_verification_email,
)
from orders.models import Order
from vendor.forms import VendorForm
from vendor.models import Vendor
from .forms import UserForm
from .models import User, UserProfile


def check_role_vendor(user):
    if user.role == 1 or (user.role is None and user.is_admin):
        return True
    else:
        raise PermissionDenied


def check_role_customer(user):
    if user.role == 2 or (user.role is None and user.is_admin):
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("myAccount")
    elif request.method == "POST":
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

            mail_subject = "Activate your FoodOnline account"
            email_template_name = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template_name)

            messages.success(request, "User registered successfully")
            return redirect("registerUser")
        else:
            messages.error(request, "User registration failed")
    else:
        form = UserForm()

    context = {"form": form}
    return render(request, "accounts/registerUser.html", context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("myAccount")
    elif request.method == "POST":
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
            vendor_name = vendor_form.cleaned_data["vendor_name"]
            vendor.vendor_slug = slugify(vendor_name) + "-" + str(user.id)
            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()

            mail_subject = "Activate your FoodOnline account"
            email_template_name = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template_name)

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


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully")
        return redirect("myAccount")
    else:
        messages.error(request, "Activation link is invalid")
        return redirect("myAccount")


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("myAccount")
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("myAccount")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")
    return render(request, "accounts/login.html")


def logout(request):
    auth.logout(request)
    messages.info(request, "You are now logged out")
    return redirect("login")


@login_required(login_url="login")
def myAccount(request):
    user = request.user
    redirectUrl = detect_user(user)
    return redirect(redirectUrl)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def custDashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders.order_by("-created_at")[:5]
    context = {"orders": orders, "recent_orders": recent_orders}
    return render(request, "accounts/custDashboard.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by("-created_at")
    recent_orders = orders[:5]
    total_revenue = 0
    total_revenue_this_month = 0
    for order in orders:
        total_revenue += order.get_total_by_vendor()["total"]

    total_revenue = round(total_revenue, 2)

    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=datetime.datetime.now().month)
    for order in current_month_orders:
        total_revenue_this_month += order.get_total_by_vendor()["total"]

    context = {"orders": orders, "recent_orders": recent_orders, "total_revenue": total_revenue,
               "total_revenue_this_month": total_revenue_this_month}
    return render(request, "accounts/vendorDashboard.html", context)


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            mail_subject = "Reset your FoodOnline account password"
            email_template_name = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, email_template_name)
            messages.success(request, "Password reset link has been sent to your email")
            return redirect("login")
        else:
            messages.error(request, "Email does not exist")
            return redirect("forgotPassword")
    return render(request, "accounts/forgotPassword.html")


def resetPasswordValidate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "This link has been expired")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            uid = request.session["uid"]
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/reset_password.html")
