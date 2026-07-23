from django.test import TestCase
from django.urls import reverse, resolve
from home.views import HomeView, AboutView


class TestUrls(TestCase):
    def test_home(self):
        urls = reverse('home:home') #/
        self.assertEqual(resolve(urls).func.view_class, HomeView)

    def test_about(self):
        urls = reverse('home:about', args=('sina',))  #/about/sina
        self.assertEqual(resolve(urls).func.view_class, AboutView)