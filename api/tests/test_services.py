from django.test import TestCase
from api.services import create_user
from unittest import mock
from django.contrib.auth.models import User


class CreateUserServiceTest(TestCase):

    @mock.patch("api.services.send_activation_email")
    def test_create_user_successfully(self, mock_send_activation_email):
        user = create_user(email="sina@email.com", username="sina", password="sinapass")

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "sina@email.com")
        self.assertEqual(user.username, "sina")
        self.assertTrue(User.objects.filter(email="sina@email.com").exists())

    @mock.patch("api.services.send_activation_email")
    def test_password_is_hashed(self, mock_send_activation_email):
        user = create_user(email="sina@email.com", username="sina", password="sinapass")

        self.assertTrue(user.check_password("sinapass"))
        self.assertNotEqual(user.password, "sinapass")

    @mock.patch("api.services.send_activation_email")
    def test_user_is_inactive_after_creation(self, mock_send_activation_email):
        user = create_user(email="sina@email.com", username="sina", password="sinapass")

        self.assertFalse(user.is_active)

    @mock.patch("api.services.send_activation_email")
    def test_activation_email_is_sent(self, mock_send_activation_email):
        user = create_user(email="sina@email.com", username="sina", password="sinapass")

        mock_send_activation_email.assert_called_once_with(user)

    @mock.patch("api.services.send_activation_email")
    def test_duplicate_user_info_raises_error(self, mock_send_activation_email):
        create_user(email="sina@email.com", username="sina", password="sinapass")

        with self.assertRaises(Exception):
            create_user(email="sina@email.com", username="sina", password="sinapass")
