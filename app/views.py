from django.shortcuts import render, redirect
from django.views import View
from app.EmailBackend import EmailBackend
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db import IntegrityError
from app.forms import CommunitySignupForm, ProfileUpdateForm
from django.core.exceptions import ValidationError
import logging
from app.models import Alumni, Student

CustomUser = get_user_model()
logger = logging.getLogger(__name__)


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
        try:
            with transaction.atomic():
                user = form.save()
                if user.user_type == '3':
                    Alumni.objects.create(admin=user, gender='')
                else:
                    Student.objects.create(user=user, gender='')
        except IntegrityError:
            messages.error(request, 'This username or email is already registered. Please sign in or choose another.')
            return redirect('register')
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
    alumni = Alumni.objects.filter(admin=request.user).first() if request.user.user_type == '3' else None
    initial = {'map_country': alumni.map_country, 'map_visible': alumni.map_visible} if alumni else {}
    form = ProfileUpdateForm(instance=request.user, initial=initial)
    return render(request, 'profile.html', {'form': form, 'is_alumni': request.user.user_type == '3'})


@login_required(login_url='/login')
def profileUpdate(request):
    if request.method != 'POST':
        return redirect('profile')
    form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                password = form.cleaned_data['password']
                if password:
                    user.set_password(password)
                user.save()
                if user.user_type == '3':
                    alumni, _ = Alumni.objects.get_or_create(admin=user, defaults={'gender': ''})
                    alumni.map_country = form.cleaned_data['map_country']
                    alumni.map_visible = form.cleaned_data['map_visible']
                    alumni.save(update_fields=['map_country', 'map_visible', 'updated_at'])
            if password:
                update_session_auth_hash(request, user)
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        except ValidationError as exc:
            form.add_error('profile_pic', exc)
        except Exception:
            logger.exception('Profile update failed for user %s', request.user.pk)
            form.add_error(None, 'Your profile could not be saved. Please try again.')
    return render(request, 'profile.html', {'form': form, 'is_alumni': request.user.user_type == '3'})
