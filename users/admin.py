from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'phone', 'city', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'city']
    ordering = ['email']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields':
                (
                    'phone',
                    'city',
                    'avatar'
                )
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'phone',
                'city',
                'avatar'
            )
        }),
    )
