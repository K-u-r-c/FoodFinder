import simplejson as json
from django.http import HttpResponse
from django.shortcuts import render, redirect

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from orders.forms import OrderForm
from orders.models import Order, Payment
from orders.utils import generate_order_number


def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("date_added")
    if cart_items.count() <= 0:
        return redirect("marketplace")

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
            order.payment_method = request.POST["payment_method"]
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
            context = {"order": order, "cart_items": cart_items}
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)

    return render(request, "orders/place_order.html")


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

    return HttpResponse("Payments")
