from home.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def create_user(*, email, username, password):
    user = User(email=email, username=username)
    user.set_password(password)
    user.is_active = False
    user.save()
    send_activation_email(user)
    return user


def update_profile(*, user, username):
    user.username = username
    user.save(update_fields=['username'])
    return user


def change_password(*, user, new_password):
    user.set_password(new_password)
    user.save(update_fields=['password'])
    return user


def deactivate_user(*, user):
    user.is_active = False
    user.save(update_fields=['is_active'])
    return user


def send_activation_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"http://localhost:8000/activate/{uid}/{token}/"
    send_mail(subject="Activate your account", message=activation_link, from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email])


def build_reset_password_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"http://127.0.0.1:8000/accounts/reset-password/{uid}/{token}/"


def send_reset_password_email(*, user, reset_url):
    html_content = render_to_string('accounts/reset_password.html', {'reset_url': reset_url})
    email = EmailMultiAlternatives(subject='Reset Password', body=f"Reset Your Password {reset_url}", from_email=settings.EMAIL_HOST_USER, to=[user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
