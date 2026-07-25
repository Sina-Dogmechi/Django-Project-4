from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import mock
from django.contrib.auth.models import User


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
