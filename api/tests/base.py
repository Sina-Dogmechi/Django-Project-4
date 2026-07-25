from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class BaseAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="sina@email.com", username="sina", password="sinapass")
        cls.admin = User.objects.create_superuser(email="admin@email.com", username="admin", password="adminpass")

    def login_user(self):
        self.client.force_authenticate(user=self.user)

    def login_admin(self):
        self.client.force_authenticate(user=self.admin)

    def logout(self):
        self.client.force_authenticate(user=None)
