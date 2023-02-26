from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from images.models import Tier, Size, Image
import tempfile
from django.core.files import File
import base64
from PIL import Image as PIL_Image
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta


class UserAuthTestCases(APITestCase):

    def test_register_new_user(self):
        payload = {
            'username': 'TestName',
            'password': 'test-user-password123',
        }
        res = self.client.post(reverse('user-list'), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', res.data)
        self.assertEqual(res.data['username'], payload['username'])

    def test_register_new_user_with_existing_username(self):
        get_user_model().objects.create_user(username='TestName', password='test-user-password123')
        payload = {
            'username': 'TestName',
            'password': 'test-user-password123',
        }
        res = self.client.post(reverse('user-list'), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', res.data)
        self.assertEqual(res.data['username'][0], 'A user with that username already exists.')

    def test_obtain_token(self):
        get_user_model().objects.create_user(username='TestName', password='test-user-password123')
        payload = {
            'username': 'TestName',
            'password': 'test-user-password123',
        }
        res = self.client.post(reverse('login'), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', res.data)

    def test_obtain_token_with_invalid_credentials(self):
        get_user_model().objects.create_user(username='TestName', password='test-user-password123')
        payload = {
            'username': 'TestName',
            'password': 'test-user-password1234',
        }
        res = self.client.post(reverse('login'), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


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


class BinaryImageTestCase(APITestCase):

    def setUp(self) -> None:
        user_details = {
            'username': 'Test Name',
            'password': 'test-user-password123',
        }
        self.user = get_user_model().objects.create_user(**user_details)
        self.client.force_authenticate(user=self.user)

        tier_details = {
            'name': 'Test',
            'original': True,
            'temporary_link': True
        }
        self.tier = Tier.objects.create(**tier_details)
        self.user.tier = self.tier
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
        self.temp_link = temp_link_res.data['temp_link']

    def test_get_binary_image(self):
        """
        Checks getting binary image success
        """
        binary_image_res = self.client.get(self.temp_link)
        self.assertEqual(binary_image_res.status_code, status.HTTP_200_OK)

        binaru_image_url = binary_image_res.data['binary_image']
        self.assertIn('http://', binaru_image_url)  # Checks if binary image url is valid

    def test_get_binary_image_wrong_link(self):
        """
        Checks getting binary image wrong link
        """
        binary_image_res = self.client.get(self.temp_link + '1')
        self.assertEqual(binary_image_res.status_code, status.HTTP_404_NOT_FOUND)

    @patch('django.utils.timezone.now', return_value=timezone.now() + timedelta(seconds=500))
    @patch('images.serializers.os.remove')
    def test_get_binary_image_expired_link(self, mock_remove, mock_now):
        """
        Checks getting binary image expired link
        """
        binary_image_res = self.client.get(self.temp_link)
        self.assertEqual(binary_image_res.status_code, status.HTTP_400_BAD_REQUEST)

