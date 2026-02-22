from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views import View


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("workout-list")
        return render(request, "registration/register.html", {"form": UserCreationForm()})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("workout-list")
        return render(request, "registration/register.html", {"form": form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("workout-list")
        return render(request, "registration/login.html", {"form": AuthenticationForm()})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.GET.get("next", "workout-list"))
        return render(request, "registration/login.html", {"form": form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("login")