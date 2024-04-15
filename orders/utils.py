import datetime


def generate_order_number(pk):
    current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{current_date}{pk}"
