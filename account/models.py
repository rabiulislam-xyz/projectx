from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from projectx.utils import phone_regex


class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True)

    phone = models.CharField(
        _('phone number'),
        max_length=17,
        validators=[phone_regex],
        blank=True)

    class Meta:
        ordering = ('username', 'email')
