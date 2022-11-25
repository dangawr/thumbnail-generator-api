from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from images.models import Tier, Size, Image
import tempfile
from django.core.files import File
import base64
from PIL import Image as PIL_Image


class PublicUser(APITestCase):

    def test_get_images_unauthorized(self):
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

    def test_upload_image(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = PIL_Image.new('RGB', (500, 500))
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

    def test_get_temp_link_permission(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = PIL_Image.new('RGB', (500, 500))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            image = Image.objects.create(original_image=File(image_file), user=self.user)
        payload = {
            'seconds_to_expire': 400,
            'image_id': image.id
        }
        temp_link_res = self.client.post(reverse('images:get-temp-link'), payload)
        self.assertEqual(temp_link_res.status_code, status.HTTP_403_FORBIDDEN)


class PremiumUser(APITestCase):

    def setUp(self) -> None:
        user_details = {
            'username': 'Test Name',
            'password': 'test-user-password123',
        }
        self.user = get_user_model().objects.create_user(**user_details)
        self.client.force_authenticate(user=self.user)

        tier_details = {
            'name': 'Enterprise',
            'original': True,
            'temporary_link': False
        }
        self.tier = Tier.objects.create(**tier_details)
        self.size_200 = Size.objects.create(size_px=200)
        self.size_400 = Size.objects.create(size_px=400)
        self.tier.sizes.add(self.size_200)
        self.tier.sizes.add(self.size_400)
        self.user.tier = self.tier

    def test_upload_image(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = PIL_Image.new('RGB', (500, 500))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'original_image': image_file}
            res = self.client.post(reverse('images:image-list'), payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('thumbnails', res.data)  # Checks if thumbnails in response

        self.assertIn('200', res.data['thumbnails'])  # Checks if correct thumbnail size in response
        self.assertIn('400', res.data['thumbnails'])

        res.data['thumbnails'].pop('200')
        res.data['thumbnails'].pop('400')
        self.assertFalse(bool(res.data['thumbnails']))  # Checks if no other thumbnails

        self.assertIn('original_image', res.data)  # Checks if original_image is in response

    def test_get_temp_link_permission(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = PIL_Image.new('RGB', (500, 500))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            image = Image.objects.create(original_image=File(image_file), user=self.user)
        payload = {
            'seconds_to_expire': 400,
            'image_id': image.id
        }
        temp_link_res = self.client.post(reverse('images:get-temp-link'), payload)
        self.assertEqual(temp_link_res.status_code, status.HTTP_403_FORBIDDEN)


class EnterpriseUser(APITestCase):

    def setUp(self) -> None:
        user_details = {
            'username': 'Test Name',
            'password': 'test-user-password123',
        }
        self.user = get_user_model().objects.create_user(**user_details)
        self.client.force_authenticate(user=self.user)

        tier_details = {
            'name': 'Enterprise',
            'original': True,
            'temporary_link': True
        }
        self.tier = Tier.objects.create(**tier_details)
        self.size_200 = Size.objects.create(size_px=200)
        self.size_400 = Size.objects.create(size_px=400)
        self.tier.sizes.add(self.size_200)
        self.tier.sizes.add(self.size_400)
        self.user.tier = self.tier

    def test_upload_image(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = PIL_Image.new('RGB', (500, 500))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'original_image': image_file}
            res = self.client.post(reverse('images:image-list'), payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('thumbnails', res.data)  # Checks if thumbnails in response

        self.assertIn('200', res.data['thumbnails'])  # Checks if correct thumbnail size in response
        self.assertIn('400', res.data['thumbnails'])

        res.data['thumbnails'].pop('200')
        res.data['thumbnails'].pop('400')
        self.assertFalse(bool(res.data['thumbnails']))  # Checks if no other thumbnails

        self.assertIn('original_image', res.data)  # Checks if original_image is in response

    def test_get_temp_link_bad_request(self):
        """
        Checks 300 < seconds < 30000 validation
        """
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = PIL_Image.new('RGB', (500, 500))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            image = Image.objects.create(original_image=File(image_file), user=self.user)
        payload = {
            'seconds_to_expire': 1,
            'image_id': image.id
        }
        res = self.client.post(reverse('images:get-temp-link'), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_binary_image(self):
        """
        Checks getting binary image success
        """
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = PIL_Image.new('RGB', (500, 500))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            image = Image.objects.create(original_image=File(image_file), user=self.user)
        payload = {
            'seconds_to_expire': 400,
            'image_id': image.id
        }
        temp_link_res = self.client.post(reverse('images:get-temp-link'), payload)
        self.assertEqual(temp_link_res.status_code, status.HTTP_201_CREATED)  # Checks getting temporary link

        binary_res = self.client.get(temp_link_res.data['temp_link'])  # Send request to temporary link

        binary_image_source = base64.b64encode(image.original_image.read())
        self.assertEqual(binary_image_source, binary_res.data['binary_image'])  # Check if binary source image is equal to image from response

