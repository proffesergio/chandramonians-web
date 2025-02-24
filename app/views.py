import profile

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from app.EmailBackend import EmailBackend
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import CustomUser

# Create your views here.
def doLogin(request):
    if request.method == "POST":
        user = EmailBackend.authenticate(
            request,
            username=request.POST.get('email'),
            password=request.POST.get('password')
        )
        if user != None:
            login(request, user)
            user_type = user.user_type
            if user_type == '1':
                return redirect('hod_home')
            elif user_type == '2':
                return redirect('staff_home')
            elif user_type == '3':
                return redirect('alumni_home')
            else:
                # message
                messages.error(request, 'Wrong Credentials! Try Again.')
                return redirect('login')
        else:
            # message
            messages.error(request, 'Wrong Credentials! Try Again.')
            return redirect('login')

def homeView(request):
    return render(request, 'hod/home.html')

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

def doLogout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/')
def profileView(request):
    user = CustomUser.objects.get(id = request.user.id)
    print(user)

    context = {
        'user':user,
    }
    return render (request, 'profile.html', context)
#
# def index(request):
#     return render('app/base.html')


# def add_alumni(request):
#     return render('templates/index.html')
@login_required(login_url='/')
def profileUpdate(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # username = request.POST.get('username')
        # email = request.POST.get('email')
        password = request.POST.get('password')
        # print(profile_pic, first_name, last_name, email, username, password)
        try:
            customUser = CustomUser.objects.get(username = request.user.username)
            # customUser = CustomUser.objects.get( id = request.user.id)

            customUser.first_name = first_name
            customUser.last_name = last_name
            customUser.profile_pic = profile_pic

            if password != None and password != "":
                customUser.set_password(password)
            if profile_pic != None and profile != "":
                customUser.profile_pic = profile_pic
            customUser.save()
            messages.success(request, 'Successfully Updated Profile!')
            return redirect('profile')
        except:
            messages.error(request, 'Error! Failed to update profile data.')
    return render(request, 'profile.html')