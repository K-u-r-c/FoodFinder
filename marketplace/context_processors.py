from menu.models import FoodItem
from .models import Cart, Tax


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
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            food_item = FoodItem.objects.get(id=item.food_item.id)
            subtotal += food_item.price * item.quantity

        get_tax = Tax.objects.filter(is_active=True)
        for tax_item in get_tax:
            tax_type = tax_item.tax_type
            tax_percentage = tax_item.tax_percentage
            tax_amount = round((subtotal * tax_percentage) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        tax = sum(x for key in tax_dict.values() for x in key.values())

        # loop over all tax items and print them
        for key, value in tax_dict.items():
            print(key, value)

        total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, total=total, tax_dict=tax_dict)
