from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from images.models import Tier, Size
import tempfile
import os

from PIL import Image


class PublicUser(APITestCase):

    def test_get_images_fail(self):
        response = self.client.get(reverse('images:image-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BasicUser(APITestCase):

    def setUp(self) -> None:
        user_details = {
            'username': 'Test Name',
            'password': 'test-user-password123',
        }
        self.user = get_user_model().objects.create_user(**user_details)
        self.client.force_authenticate(user=self.user)

        tier_details = {
            'name': 'Basic',
            'original': False,
            'temporary_link': False
        }
        self.tier = Tier.objects.create(**tier_details)
        self.size_200 = Size.objects.create(size_px=200)
        self.tier.sizes.add(self.size_200)
        self.user.tier = self.tier

    def tearDown(self) -> None:
        pass

    def test_upload_image(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (500, 500))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'original_image': image_file}
            res = self.client.post(reverse('images:image-list'), payload, format='multipart')
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertIn('thumbnails', res.data)   # Checks if thumbnails in response
            self.assertIn('200', res.data['thumbnails'])  # Checks if correct thumbnail size in response
            res.data['thumbnails'].pop('200')
            self.assertFalse(bool(res.data['thumbnails']))  # Checks if no other thumbnails
            self.assertNotIn('original_image', res.data)  # Checks if original_image is not in response

