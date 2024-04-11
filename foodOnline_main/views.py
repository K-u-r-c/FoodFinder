from django.shortcuts import render
from foodOnline_main.utils import get_or_set_current_location
from vendor.models import Vendor
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


def home(request):
    if get_or_set_current_location(request) is not None:
        point = GEOSGeometry("POINT(%s %s)" % get_or_set_current_location(request))

        vendors = (
            Vendor.objects.filter(
                user_profile__location__distance_lte=(point, D(km=1000000)),
            )
            .annotate(distance=Distance("user_profile__location", point))
            .order_by("distance")
        )

        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {"vendors": vendors}
    return render(request, "home.html", context)
