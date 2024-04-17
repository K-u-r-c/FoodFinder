import simplejson as json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.utils import send_notification
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderedFood
from orders.utils import generate_order_number


@login_required(login_url="login")
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("date_added")
    if cart_items.count() <= 0:
        return redirect("marketplace")

    vendors_ids = []
    for item in cart_items:
        if item.food_item.vendor.id not in vendors_ids:
            vendors_ids.append(item.food_item.vendor.id)

    total_data = {}
    subtotal = 0
    k = {}
    get_tax = Tax.objects.filter(is_active=True)
    for item in cart_items:
        food_item = FoodItem.objects.get(id=item.food_item.id, vendor_id__in=vendors_ids)
        v_id = food_item.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += food_item.price * item.quantity
            k[v_id] = subtotal
        else:
            subtotal = food_item.price * item.quantity
            k[v_id] = subtotal

        tax_dict = {}
        for tax_item in get_tax:
            tax_type = tax_item.tax_type
            tax_percentage = tax_item.tax_percentage
            tax_amount = round((subtotal * tax_percentage) / 100, 2)
            tax_dict = {tax_type: {str(tax_percentage): str(tax_amount)}}

        total_data.update({v_id: {str(subtotal): str(tax_dict)}})

    subtotal = get_cart_amounts(request)["subtotal"]
    tax = get_cart_amounts(request)["tax"]
    total = get_cart_amounts(request)["total"]
    tax_dict = get_cart_amounts(request)["tax_dict"]

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.email = form.cleaned_data["email"]
            order.phone = form.cleaned_data["phone"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.city = form.cleaned_data["city"]
            order.pin_code = form.cleaned_data["pin_code"]
            order.user = request.user
            order.total = total
            order.tax_data = json.dumps(tax_dict)
            order.total_tax = tax
            order.total_data = json.dumps(total_data)
            order.payment_method = request.POST["payment_method"]
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
            context = {"order": order, "cart_items": cart_items}
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)

    return render(request, "orders/place_order.html")


@login_required(login_url="login")
def payments(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" and request.method == "POST":
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.food_item
            ordered_food.quantity = item.quantity
            ordered_food.price = item.food_item.price
            ordered_food.amount = item.food_item.price * item.quantity
            ordered_food.save()

        mail_subject = "Thank you for your order"
        mail_template = "orders/order_confirmation_email.html"
        context = {"user": request.user, "order": order, "to_email": order.email}
        send_notification(mail_subject, mail_template, context)

        mail_subject = "New order received"
        mail_template = "orders/new_order_email.html"

        to_emails = []
        for item in cart_items:
            if item.food_item.vendor.user.email not in to_emails:
                to_emails.append(item.food_item.vendor.user.email)

        context = {"order": order, "to_email": to_emails}
        send_notification(mail_subject, mail_template, context)

        cart_items.delete()
        response = {
            "success": "Payment Successful",
            "order_number": order.order_number,
            "transaction_id": transaction_id
        }
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"})


def order_complete(request):
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("transaction_id")
    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += item.price * item.quantity

        tax_data = json.loads(order.tax_data)
        total = order.total

        context = {"order": order, "ordered_food": ordered_food, "subtotal": subtotal, "tax_data": tax_data,
                   "total": total}
        return render(request, "orders/order_complete.html", context)
    except:  # noqa
        return redirect("home")
