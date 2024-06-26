from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserProfile
from marketplace.context_processors import get_cart_amounts, get_cart_counter
from marketplace.models import Cart
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from vendor.models import Vendor, OpeningHour


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    context = {"vendors": vendors}
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("fooditems", queryset=FoodItem.objects.filter(is_available=True))
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by("day", "-from_hour")

    today = date.today().isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {"vendor": vendor, "categories": categories, "cart_items": cart_items, "opening_hours": opening_hours,
               "current_opening_hours": current_opening_hours}
    return render(request, "marketplace/vendor_detail.html", context)


@login_required(login_url="login")
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("date_added")
    context = {"cart_items": cart_items}
    return render(request, "marketplace/cart.html", context)


@login_required(login_url="login")
def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            try:
                food_item = FoodItem.objects.get(id=food_id)
                try:
                    checkCart = Cart.objects.get(user=request.user, food_item=food_item)
                    checkCart.quantity += 1
                    checkCart.save()
                    return JsonResponse(
                        {
                            "success": "Item added to cart",
                            "cart_counter": get_cart_counter(request),
                            "cart_item_quantity": checkCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
                except Cart.DoesNotExist:
                    newCart = Cart.objects.create(
                        user=request.user, food_item=food_item, quantity=1
                    )
                    newCart.save()
                    return JsonResponse(
                        {
                            "success": "Item added to cart and new cart created",
                            "cart_counter": get_cart_counter(request),
                            "cart_item_quantity": newCart.quantity,
                            "cart_amount": get_cart_amounts(request),
                        }
                    )

            except FoodItem.DoesNotExist:
                return JsonResponse({"error": "Food item not found"})
        else:
            return JsonResponse({"error": "This URL only supports AJAX requests"})
    else:
        return JsonResponse({"error": "You must be logged in to add to cart"})


@login_required(login_url="login")
def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            try:
                food_item = FoodItem.objects.get(id=food_id)
                try:
                    checkCart = Cart.objects.get(user=request.user, food_item=food_item)
                    if checkCart.quantity > 1:
                        checkCart.quantity -= 1
                        checkCart.save()
                        return JsonResponse(
                            {
                                "success": "Item quantity decreased",
                                "cart_counter": get_cart_counter(request),
                                "cart_item_quantity": checkCart.quantity,
                                "cart_amount": get_cart_amounts(request),
                            }
                        )
                    else:
                        checkCart.quantity = 0
                        checkCart.delete()
                        return JsonResponse(
                            {
                                "success": "Item removed from cart",
                                "cart_counter": get_cart_counter(request),
                                "cart_item_quantity": checkCart.quantity,
                                "cart_amount": get_cart_amounts(request),
                            }
                        )
                except Cart.DoesNotExist:
                    return JsonResponse({"error": "Item not found in cart"})
            except FoodItem.DoesNotExist:
                return JsonResponse({"error": "Food item not found"})
        else:
            return JsonResponse({"error": "This URL only supports AJAX requests"})
    else:
        return JsonResponse({"error": "You must be logged in to decrease cart"})


@login_required(login_url="login")
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            try:
                cart_item = Cart.objects.get(id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse(
                        {
                            "success": "Item removed from cart",
                            "cart_counter": get_cart_counter(request),
                            "cart_amount": get_cart_amounts(request),
                        }
                    )
            except Cart.DoesNotExist:
                return JsonResponse({"error": "Item not found in cart"})
        else:
            return JsonResponse({"error": "This URL only supports AJAX requests"})
    else:
        return JsonResponse({"error": "You must be logged in to delete cart"})


def search(request):
    if "address" not in request.GET:
        return redirect("marketplace")
    else:
        address = request.GET["address"]
        latitude = request.GET["lat"]
        longitude = request.GET["lng"]
        radius = request.GET["radius"]
        restaurant_name = request.GET["restaurant_name"]

        fetch_vendors_by_food_item = FoodItem.objects.filter(
            name__icontains=restaurant_name, is_available=True
        ).values_list("vendor", flat=True)

        if latitude and longitude and radius:
            point = GEOSGeometry(f"POINT({longitude} {latitude})")

            vendors = (
                Vendor.objects.filter(
                    Q(id__in=fetch_vendors_by_food_item)
                    | Q(vendor_name__icontains=restaurant_name),
                    is_approved=True,
                    user__is_active=True,
                    user_profile__location__distance_lte=(point, D(km=radius)),
                )
                .annotate(distance=Distance("user_profile__location", point))
                .order_by("distance")
            )

            for vendor in vendors:
                vendor.kms = round(vendor.distance.km, 1)

        else:
            vendors = Vendor.objects.filter(
                Q(id__in=fetch_vendors_by_food_item)
                | Q(vendor_name__icontains=restaurant_name),
                is_approved=True,
                user__is_active=True,
            )

        context = {
            "vendors": vendors,
            "vendor_count": vendors.count(),
            "address": address,
        }

        return render(request, "marketplace/listings.html", context)


@login_required(login_url="login")
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("date_added")
    if cart_items.count() <= 0:
        return redirect("marketplace")

    user_profile = UserProfile.objects.get(user=request.user)
    initial_values = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "phone": request.user.phone_number,
        "address": user_profile.address,
        "country": user_profile.country,
        "city": user_profile.city,
        "pin_code": user_profile.pin_code,
    }
    form = OrderForm(initial=initial_values)

    context = {"form": form, "cart_items": cart_items}
    return render(request, "marketplace/checkout.html", context)
