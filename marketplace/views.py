from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from marketplace.context_processors import get_cart_counter
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    context = {"vendors": vendors}
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("fooditems", queryset=FoodItem.objects.filter(is_available=True))
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {"vendor": vendor, "categories": categories, "cart_items": cart_items}
    return render(request, "marketplace/vendor_detail.html", context)


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
                        }
                    )

            except FoodItem.DoesNotExist:
                return JsonResponse({"error": "Food item not found"})
        else:
            return JsonResponse({"error": "This URL only supports AJAX requests"})
    else:
        return JsonResponse({"error": "You must be logged in to add to cart"})


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
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    context = {"cart_items": cart_items}
    return render(request, "marketplace/cart.html", context)


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
                        }
                    )
            except Cart.DoesNotExist:
                return JsonResponse({"error": "Item not found in cart"})
        else:
            return JsonResponse({"error": "This URL only supports AJAX requests"})
    else:
        return JsonResponse({"error": "You must be logged in to delete cart"})
