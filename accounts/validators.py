from django.core.exceptions import ValidationError


def allow_only_images_validator(value):
    try:
        if not value.name.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            raise ValidationError("Only images are allowed")
    except AttributeError:
        raise ValidationError("Invalid file")
