from django.test import TestCase
from api.services import create_user, update_profile, change_password, build_reset_password_link
from unittest import mock
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


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


class UpdateProfileServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sina@email.com", username="sina", password="sinapass")

    def test_update_username_successfully(self):
        user = update_profile(user=self.user, username="jack")

        self.user.refresh_from_db()

        self.assertEqual(self.user.username, "jack")
        self.assertEqual(user.username, "jack")

    def test_return_update_user(self):
        user = update_profile(user=self.user, username="jack")

        self.assertEqual(user.pk, self.user.pk)

    def test_email_does_not_change(self):
        old_email = self.user.email
        update_profile(user=self.user, username="jack")

        self.user.refresh_from_db()

        self.assertEqual(self.user.email, old_email)

    def test_only_username_is_updated(self):
        old_password = self.user.password
        update_profile(user=self.user, username="jack")

        self.user.refresh_from_db()

        self.assertEqual(self.user.password, old_password)
        self.assertTrue(self.user.check_password("sinapass"))


class ChangePasswordServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sina@email.com", username="sina", password="sinapass")

    def test_change_password_successfully(self):
        user = change_password(user=self.user, new_password="new_pass")

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("new_pass"))
        self.assertEqual(user.pk, self.user.pk)

    def test_old_password_is_not_valid(self):
        change_password(user=self.user, new_password="new_pass")

        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password("sinapass"))

    def test_password_is_hashed(self):
        change_password(user=self.user, new_password="new_pass")

        self.user.refresh_from_db()

        self.assertNotEqual(self.user.password, "new_pass")
        self.assertTrue(self.user.password.startswith("pbkdf2_"))

    def test_return_updated_user(self):
        user = change_password(user=self.user, new_password="new_pass")

        self.assertIsInstance(user, User)
        self.assertEqual(user.id, self.user.id)

    def test_only_password_is_updated(self):
        old_username = self.user.username
        old_email = self.user.email
        change_password(user=self.user, new_password="new_pass")

        self.user.refresh_from_db()

        self.assertEqual(self.user.username, old_username)
        self.assertEqual(self.user.email, old_email)


class BuildResetPasswordLinkServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sina@email.com", username="sina", password="sinapass")

    def test_build_reset_password_link_successfully(self):
        link = build_reset_password_link(self.user)

        self.assertIsInstance(link, str)
        self.assertNotEqual(link, "")

    def test_link_contains_uid(self):
        link = build_reset_password_link(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        self.assertIn(uid, link)

    def test_link_contains_token(self):
        link = build_reset_password_link(self.user)
        token = default_token_generator.make_token(self.user)

        self.assertIn(token, link)

    def test_link_contains_reset_password_path(self):
        link = build_reset_password_link(self.user)

        self.assertIn("/accounts/reset-password/", link)
