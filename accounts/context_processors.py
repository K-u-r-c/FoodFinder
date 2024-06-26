from accounts.models import UserProfile
from foodOnline_main import settings
from vendor.models import Vendor


def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Exception:
        vendor = None
    return dict(vendor=vendor)


def get_user_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except Exception:
        user_profile = None
    return dict(user_profile=user_profile)


def get_google_api_key(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_MAPS_API_KEY}


def get_paypal_client_id(request):
    return {'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID}
