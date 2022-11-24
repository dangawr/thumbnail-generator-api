from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Image)
admin.site.register(models.Tier)
admin.site.register(models.Size)
admin.site.register(models.User)
