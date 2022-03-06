import re

from django.core.validators import RegexValidator
from django.db.models import Model
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


def generate_slug(instance: Model, value: str) -> str:
    slug = re.sub(r'[-\s]+', '-', value.lower()).strip()

    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + '-' + get_random_string(length=4)
    return unique_slug


phone_regex = RegexValidator(
    regex=r'^(?:\+88|88)?(0(1|9)[3-9]\d{7,10})$',
    message=_("Must be a valid phone number of bangladesh"))
