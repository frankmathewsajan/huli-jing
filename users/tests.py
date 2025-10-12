from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
import time

class UserAuthTests(APITestCase):

    def setUp(self):
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:token_obtain_pair')
        self.refresh_url = reverse('users:token_refresh')
        self.verify_url = reverse('users:token_verify')
        self.blacklist_url = reverse('users:token_blacklist')

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123"
        }

    # --------------------
    # Registration Tests
    # --------------------
    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_user_missing_field(self):
        data = {"username": "noemail"}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_username(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_user_invalid_email(self):
        data = {**self.user_data, "email": "invalid-email"}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_user_weak_password(self):
        data = {**self.user_data, "password": "123"}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------
    # Login Tests
    # --------------------
    def test_login_user_success(self):
        User.objects.create_user(**self.user_data)
        login_data = {"username": "testuser", "password": "strongpassword123"}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]

    def test_login_user_wrong_password(self):
        User.objects.create_user(**self.user_data)
        login_data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_user_nonexistent(self):
        login_data = {"username": "doesnotexist", "password": "whatever"}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # JWT Refresh Tests
    # --------------------
    def test_refresh_token_success(self):
        self.test_login_user_success()
        response = self.client.post(self.refresh_url, {"refresh": self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_invalid(self):
        response = self.client.post(self.refresh_url, {"refresh": "fake_token"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_as_access(self):
        self.test_login_user_success()
        # Using access token in refresh endpoint should fail
        response = self.client.post(self.refresh_url, {"refresh": self.access_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # JWT Verify Tests
    # --------------------
    def test_verify_token_success(self):
        self.test_login_user_success()
        response = self.client.post(self.verify_url, {"token": self.access_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_token_invalid(self):
        response = self.client.post(self.verify_url, {"token": "fake_token"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_tampered_token(self):
        self.test_login_user_success()
        tampered = self.access_token[:-1] + ('a' if self.access_token[-1] != 'a' else 'b')
        response = self.client.post(self.verify_url, {"token": tampered}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # Blacklist Tests
    # --------------------
    def test_blacklist_token_success(self):
        self.test_login_user_success()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.blacklist_url, {"refresh": self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_blacklist_token_missing_refresh(self):
        self.test_login_user_success()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.blacklist_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blacklist_token_invalid_refresh(self):
        self.test_login_user_success()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.blacklist_url, {"refresh": "fake_token"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blacklist_token_double(self):
        self.test_login_user_success()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.client.post(self.blacklist_url, {"refresh": self.refresh_token}, format='json')
        response = self.client.post(self.blacklist_url, {"refresh": self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blacklist_no_auth_header(self):
        self.test_login_user_success()
        # Missing Authorization header
        response = self.client.post(self.blacklist_url, {"refresh": self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

