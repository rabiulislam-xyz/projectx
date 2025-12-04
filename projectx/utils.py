import re
from collections import OrderedDict

from django.core.validators import RegexValidator
from django.db.models import Model
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from rest_framework import pagination
from rest_framework.pagination import _positive_int
from rest_framework.response import Response

from utils.misc import convert_to_bool


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


class PageNumberPagination10(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 10


class LimitOffsetPagination10(pagination.LimitOffsetPagination):
    limit_query_param = 'length'
    offset_query_param = 'start'
    default_limit = 10
    max_limit = 999999

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('recordsTotal', 0),
            ('recordsFiltered', self.count),
            ('data', data)
        ]))


class LimitOffsetPagination10v2(pagination.LimitOffsetPagination):
    limit_query_param = 'length'
    offset_query_param = 'start'
    default_limit = 10
    max_limit = 999999

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        # send all data if request is from app
        if request.headers.get('fromApp') and convert_to_bool(request.headers.get('fromApp')):
            return self.max_limit

        return self.default_limit

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('recordsTotal', 0),
            ('recordsFiltered', self.count),
            ('data', data)
        ]))


class LimitOffsetPagination100(pagination.LimitOffsetPagination):
    limit_query_param = 'length'
    offset_query_param = 'start'
    default_limit = 100
    max_limit = 999999

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('recordsTotal', 0),
            ('recordsFiltered', self.count),
            ('data', data)
        ]))
