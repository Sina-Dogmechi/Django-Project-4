from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from home.forms import UserRegistrationFrom


class UserRegistrationFromTest(TestCase):
    def setUp(self):
        self.url = reverse('home:user_register') #/register/
        self.user = User.objects.create_user(username="sina", email="sina@email.com", password="sina")

    def test_register_authenticated_user_redirects(self):
        self.client.login(username="sina", password="sina")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("home:home"))

    def test_register_GET_anonymous_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/register.html")
        self.assertTrue(response.context["form"], UserRegistrationFrom)

    def test_register_POST_valid_data(self):
        response = self.client.post(self.url, {"username":"jack", "email":"jack@email.com", "password1":"jackpass", "password2":"jackpass"})

        self.assertRedirects(response, reverse("home:home"))
        self.assertTrue(User.objects.filter(username="jack").exists())

    def test_register_POST_invalid_data(self):
        response = self.client.post(self.url, {"username":"jack", "email":"invalid_email", "password1":"jackpass", "password2":"jackpass"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertFalse(response.context["form"].is_valid())
        self.assertFormError(form=response.context["form"], field="email", errors="Enter a valid email address.")
