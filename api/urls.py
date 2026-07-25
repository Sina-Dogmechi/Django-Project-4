from django.urls import path
from . import views


app_name = 'api'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.UserChangePasswordView.as_view(), name='change_password'),
    path('deactivate/<int:pk>/',views.UserDeactivateView.as_view(), name='deactivate'),
]