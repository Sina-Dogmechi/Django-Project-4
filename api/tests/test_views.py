from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import mock
from django.contrib.auth.models import User
from .base import BaseAPITestCase


class UserRegisterViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("api:register")

    @mock.patch("api.views.create_user")
    def test_register_successfully(self, mock_create_user): # unittest
        user = User(email="sina@email.com", username="sina", password="sinapass")
        mock_create_user.return_value = user
        response = self.client.post(self.url, {
            "email": "sina@email.com",
            "username": "sina",
            "password": "sinapass",
            "password2": "sinapass"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "sina@email.com")
        mock_create_user.assert_called_once_with(email="sina@email.com", username="sina", password="sinapass")

    def test_register_with_invalid_data(self):
        response = self.client.post(self.url, {
            "email": "sina-email",
            "username": "",
            "password": "sinapass",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password2", response.data)

    def test_user_created_in_database(self): # Integration test
        response = self.client.post(self.url, {
            "email": "sina@email.com",
            "username": "sina",
            "password": "sinapass",
            "password2": "sinapass"
        }, format="json")

        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(email="sina@email.com").exists())


class UserProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sina@email", username="sina", password="sinapass")
        self.url = reverse("api:profile")

    def test_profile_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_successfully(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["username"], self.user.username)

    @mock.patch("api.views.update_profile")
    def test_update_profile_successfully(self, mock_update_profile):
        self.client.force_authenticate(user=self.user)
        self.user.username = "new_username"
        mock_update_profile.return_value = self.user
        response = self.client.put(self.url, {"username": "new_username"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "new_username")
        mock_update_profile.assert_called_once_with(user=self.user, username="new_username")

    def test_update_profile_requires_authentication(self):
        response = self.client.put(self.url, {"username": "new_name"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserChangePasswordViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sina@email.com", username="sina", password="sinapass")
        self.url = reverse("api:change_password")

    def test_change_password_requires_authentication(self):
        response = self.client.patch(self.url, {"new_password": "sinanewpass"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch("api.views.change_password")
    def test_change_password_successfully(self, mock_change_password):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {"new_password": "sinanewpass"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_change_password.assert_called_once_with(user=self.user, new_password="sinanewpass")

    def test_change_password_with_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {"new_password": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch("api.views.change_password")
    def test_change_password_calls_service_once(self, mock_change_password):
        self.client.force_authenticate(user=self.user)
        self.client.patch(self.url, {"new_password": "sinanewpass"}, format="json")

        self.assertEqual(mock_change_password.call_count, 1)

    def test_change_password_in_database(self): # Integration Test
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {"new_password": "sinanewpass"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("sinanewpass"))


class UserDeactivateViewTest(BaseAPITestCase):
    def setUp(self):
        self.url = reverse("api:deactivate", args=[self.user.id])

    def test_anonymous_user_cannot_deactivate_user(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_normal_user_cannot_deactivate_user(self):
        self.login_user()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    @mock.patch("api.views.deactivate_user")
    def test_admin_can_deactivate_user(self, mock_deactivate):
        self.login_admin()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_deactivate.assert_called_once_with(user=self.user)

    def test_user_not_found(self):
        self.login_admin()
        response = self.client.post(reverse("api:deactivate", args=[9999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "user not found")

    def test_user_becomes_inactive(self): # Integration Test
        self.login_admin()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class UserForgotPasswordViewTest(BaseAPITestCase):
    def setUp(self):
        self.url = reverse("api:forgot_password")

    def test_anonymous_user_can_send_request(self): # Unittest - Authentication
        response = self.client.post(self.url, {"email":"sina@email.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_email(self): # Unittest - Validation
        response = self.client.post(self.url, {"email":"wrong-email"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    @mock.patch("api.views.send_reset_password_email")
    @mock.patch("api.views.build_reset_password_link")
    @mock.patch("api.views.get_user_by_email")
    def test_send_reset_email_successfully(self, mock_get_user, mock_build_link, mock_send_email):
        mock_get_user.return_value = self.user
        mock_build_link.return_value = "http://test/reset"
        response = self.client.post(self.url, {"email":self.user.email}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_user.assert_called_once_with(email=self.user.email)
        mock_build_link.assert_called_once_with(self.user)
        mock_send_email.assert_called_once_with(user=self.user, reset_url="http://test/reset")

    @mock.patch("api.views.send_reset_password_email")
    @mock.patch("api.views.get_user_by_email")
    def test_email_not_sent_for_unknown_user(self, mock_get_user, mock_send_email):
        mock_get_user.return_value = None
        response = self.client.post(self.url, {"email":"unknown@email.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_not_called()

    def test_existing_user_receives_success_response(self): # Integration Test
        response = self.client.post(self.url, {"email":self.user.email}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "a reset link has been sent.")

    def test_unknown_user_receives_success_response(self): # Integration Test
        response = self.client.post(self.url, {"email":"unknown@email.com"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "a reset link has been sent.")
