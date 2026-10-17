from django.shortcuts import render, redirect
from django.views import View
from app.EmailBackend import EmailBackend
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from app.forms import CommunitySignupForm
from app.models import Alumni, Student

CustomUser = get_user_model()


class RegisterView(View):
    def get(self, request):
        return render(request, 'sign-up.html')


def doRegister(request):
    if request.method == "POST":
        data = request.POST.copy()
        data.setdefault('password1', data.get('password', ''))
        data.setdefault('password2', data.get('confirm_password', ''))
        form = CommunitySignupForm(data)
        if not form.is_valid():
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
            return redirect('register')
        with transaction.atomic():
            user = form.save()
            if user.user_type == '3':
                Alumni.objects.create(admin=user, gender='')
            else:
                Student.objects.create(user=user, gender='')
        login(request, user)
        return redirect("landing")

    return render(request, "sign-up.html")


def doLogin(request):
    if request.user.is_authenticated:
        messages.warning(request, "You're already logged in!")
        return redirect('landing')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            role_redirects = {
                '1': 'hod_home',
                '2': 'staff_home',
                '3': 'alumni_home',
                '4': 'edu_home',
            }
            return redirect(role_redirects.get(user.user_type, 'landing'))
        else:
            messages.warning(request, "Invalid email or password!")

    return render(request, 'loginpage.html')


class DefaultView(View):
    def get(self, request):
        return render(request, 'userlanding.html')


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'loginpage.html')


def doLogout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login')
def profileView(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, 'profile.html', {'user': user})


@login_required(login_url='/login')
def profileUpdate(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=request.user.username)
            user.first_name = first_name
            user.last_name = last_name
            if password:
                user.set_password(password)
            if profile_pic:
                user.profile_pic = profile_pic
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        except Exception:
            messages.error(request, 'Failed to update profile. Please try again.')

    return render(request, 'profile.html')
