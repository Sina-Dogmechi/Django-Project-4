from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from home.forms import UserRegistrationFrom
from django.contrib.messages import get_messages
from home.models import Post, Relation, Profile


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


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.url = reverse("home:user_login")
        self.user = User.objects.create_user(username="sina", email="sina@email.com", password="sinapass")

    def test_login_GET_anonymous_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/login.html")

    def test_authenticated_user_redirects_to_home(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("home:home"))

    def test_login_successfully(self):
        response = self.client.post(self.url, data={"username":"sina", "password":"sinapass"})

        self.assertRedirects(response, reverse("home:home"))
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_with_wrong_password(self):
        response = self.client.post(self.url, {"username": "sina", "password": "wrong_password"})

        self.assertEqual(response.status_code, 200)
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_login_error_message(self):
        response = self.client.post(self.url, {"username": "sina", "password": "wrong_password"})
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "username/password is wrong!")

    def test_login_success_message(self):
        response = self.client.post(self.url, {"username": "sina", "password": "sinapass"})
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "you logged in successfully")

    def test_login_redirects_to_next_url(self):
        response = self.client.post(self.url + "?next=/about/sina/", {"username": "sina", "password": "sinapass"})

        self.assertRedirects(response, "/about/sina/")


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="sina", password="sinapass")
        self.user2 = User.objects.create_user(username="jack", password="jackpass")
        self.post1 = Post.objects.create(user=self.user2, body="first post", slug="first-post")
        self.post2 = Post.objects.create(user=self.user2, body="second post", slug="second-post")

        self.url = reverse("home:user_profile", args=[self.user2.id])

    def test_profile_requires_login(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('home:user_login')}?next={self.url}")

    def test_profile_loads_successfully(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/profile.html")

    def test_profile_context_contains_correct_user(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.url)

        self.assertEqual(response.context["user"], self.user2)

    def test_profile_context_contains_user_posts(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.url)
        posts = response.context["posts"]

        self.assertEqual(posts.count(), 2)
        self.assertIn(self.post1, posts)
        self.assertIn(self.post2, posts)

    def test_is_following_false(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.url)

        self.assertFalse(response.context["is_following"])

    def test_is_following_true(self):
        Relation.objects.create(from_user=self.user1, to_user=self.user2)
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.url)

        self.assertTrue(response.context["is_following"])

    def test_profile_returns_404_for_invalid_user(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(reverse("home:user_profile", args=[9999999]))

        self.assertEqual(response.status_code, 404)


class UserFollowUnfollowTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="sina", password="sinapass")
        self.user2 = User.objects.create_user(username="jack", password="jackpass")
        self.follow_url = reverse("home:user_follow", args=[self.user2.id])
        self.unfollow_url = reverse("home:user_unfollow", args=[self.user2.id])

    def test_follow_required_login(self):
        response = self.client.get(self.follow_url)
        self.assertRedirects(response, f"{reverse("home:user_login")}?next={self.follow_url}")

    def test_follow_successfully(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.follow_url)
        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, reverse("home:user_profile", args=[self.user2.id]))
        self.assertTrue(Relation.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertEqual(messages[0].message, f"you followed {self.user2.username}..!")

    def test_follow_user_twice(self):
        Relation.objects.create(from_user=self.user1, to_user=self.user2)
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.follow_url)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(Relation.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        self.assertEqual(messages[0].message, f"you already following {self.user2.username}..!")

    def test_unfollow_required_login(self):
        response = self.client.get(self.unfollow_url)
        self.assertRedirects(response, f"{reverse("home:user_login")}?next={self.unfollow_url}")

    def test_unfollow_successfully(self):
        Relation.objects.create(from_user=self.user1, to_user=self.user2)
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.unfollow_url)
        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, reverse("home:user_profile", args=[self.user2.id]))
        self.assertFalse(Relation.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertEqual(messages[0].message, f"you unfollowed {self.user2.username}..!")

    def test_unfollow_when_relation_not_exist(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.unfollow_url)
        messages = list(get_messages(response.wsgi_request))

        self.assertFalse(Relation.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.assertEqual(messages[0].message, f"you are not following {self.user2.username}..!")


class EditUserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sina", email="sina@email.com", password="sinapass")
        self.profile = Profile.objects.create(user=self.user, age=20, address="Tehran")
        self.url = reverse("home:edit_user")

    def test_edit_profile_requires_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse("home:user_login")}?next={self.url}")

    def test_edit_profile_get(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/edit_profile.html")

    def test_edit_profile_successfully(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.post(self.url, {"age": 25, "address": "Tabriz", "email": "new@email.com"})

        self.assertRedirects(response, reverse("home:user_profile", args=[self.user.id]))

        self.profile.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.profile.age, 25)
        self.assertEqual(self.profile.address, "Tabriz")
        self.assertEqual(self.user.email, "new@email.com")

    def test_success_message_after_edit(self):
        self.client.login(username="sina", password="sinapass")
        response = self.client.post(self.url, {"age": 25, "address": "Tabriz", "email": "new@email.com"})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]

        self.assertIn("profile edited successfully", messages)
