from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin


@admin.register(models.User)
class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets+ (
        (
            'User Tier',
            {
                'fields': (
                    'tier',
                ),
            },
        ),
    )


admin.site.register(models.Image)
admin.site.register(models.Tier)
admin.site.register(models.Size)
# admin.site.register(models.User, UserAdmin)
