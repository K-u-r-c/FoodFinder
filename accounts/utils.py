def detect_user(user):
    if user.role == 1:
        redirectUrl = "vendorDashboard"
    elif user.role == 2:
        redirectUrl = "custDashboard"
    elif user.role is None and user.is_admin:
        redirectUrl = "adminDashboard"
    return redirectUrl
