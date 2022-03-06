from django.contrib import admin
from django.contrib.auth.models import Permission

from account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_full_name',
                    'email', 'phone', 'date_joined']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('codename', 'name')
    list_filter = ['content_type']
    list_display = ['__str__', 'content_type', 'codename', 'name']
