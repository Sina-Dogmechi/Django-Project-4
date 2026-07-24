from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationFrom, UserLoginFrom
from django.contrib.auth import authenticate, login, logout
from .models import Relation
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(View):
    def get(self, request):
        return render(request, 'home/home.html')


class AboutView(View):
    def get(self, request, username):
        return render(request, 'home/about.html')


class UserRegisterView(View):
    form_class = UserRegistrationFrom
    template_name = 'home/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(username=cd['username'], email=cd['email'], password=cd['password1'])
            messages.success(request, "you registered successfully", "success")
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    form_class = UserLoginFrom
    template_name = 'home/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, "you logged in successfully", "success")
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, "username/password is wrong!", "warning")
        return render(request, self.template_name, {'form': form})


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        is_following = False
        user = get_object_or_404(User, pk=user_id)
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            is_following = True
        return render(request, 'home/profile.html', {'user':user, 'posts':posts, 'is_following':is_following})


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, f"you already following {user.username}..!", 'danger')
        else:
            Relation(from_user=request.user, to_user=user).save()
            messages.success(request, f"you followed {user.username}..!", 'success')
        return redirect('home:user_profile', user.id)


class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request, f"you unfollowed {user.username}..!", 'success')
        else:
            messages.error(request, f"you are not following {user.username}..!", 'danger')
        return redirect('home:user_profile', user.id)
