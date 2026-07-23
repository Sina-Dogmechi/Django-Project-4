from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationFrom, UserLoginFrom
from django.contrib.auth import authenticate, login, logout


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
