from django.urls import path
from . import views


app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/<str:username>/', views.AboutView.as_view(), name='about'),
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('profile/<int:user_id>', views.UserProfileView.as_view(), name='user_profile'),
    path('follow/<int:user_id>', views.UserFollowView.as_view(), name='user_follow'),
    path('unfollow/<int:user_id>', views.UserUnfollowView.as_view(), name='user_unfollow'),
    path('edit_user/', views.EditUserView.as_view(), name='edit_user'),
]