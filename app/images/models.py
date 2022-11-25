from django.db import models
from django.contrib.auth.models import AbstractUser
import os
import uuid
from django.conf import settings


def image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'originals', filename)


class Size(models.Model):
    size_px = models.IntegerField(default=200)

    def __str__(self):
        return str(self.size_px)


class Tier(models.Model):
    name = models.CharField(max_length=25)
    sizes = models.ManyToManyField(Size, related_name='tiers', blank=True)
    original = models.BooleanField(default=False)
    temporary_link = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.deletion.SET_NULL, related_name='users', null=True)

    def __str__(self):
        return self.username


class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.deletion.CASCADE, related_name='images')
    original_image = models.ImageField(upload_to=image_file_path)


class TemporaryLinkModel(models.Model):
    one_time_code = models.CharField(max_length=20)
    expiry_time = models.DateTimeField(blank=True)
    image = models.ForeignKey(Image, on_delete=models.deletion.CASCADE, null=True, related_name='templinks')

