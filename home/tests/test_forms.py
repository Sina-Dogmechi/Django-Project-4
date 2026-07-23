from django.test import TestCase
from home.forms import UserRegistrationFrom
from django.contrib.auth.models import User


class TestUserRegistrationFrom(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="kevin", email="kevin@email.com", password="kevinpass")

    def test_valid_data(self):
        form = UserRegistrationFrom(data={"username":"jack", "email":"jack@email.com", "password1":"jackpass", "password2":"jackpass"})
        self.assertTrue(form.is_valid())

    def test_empty_data(self):
        form = UserRegistrationFrom(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)

    def test_exist_email(self):
        form = UserRegistrationFrom(data={"username":"not-kevin", "email":"kevin@email.com", "password1":"kevinpass", "password2":"kevinpass"})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error("email"))

    def test_unmatched_passwords(self):
        form = UserRegistrationFrom(data={"username": "mark", "email": "mark@email.com", "password1": "mark1", "password2": "mark2"})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue(form.has_error)
