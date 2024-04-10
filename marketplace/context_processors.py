from menu.models import FoodItem
from .models import Cart


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for item in cart_items:
                    cart_count += item.quantity
            else:
                cart_count = 0
        except Cart.DoesNotExist:
            cart_count = 0
    return {"cart_count": cart_count}


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            food_item = FoodItem.objects.get(id=item.food_item.id)
            subtotal += food_item.price * item.quantity

        total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, total=total)
