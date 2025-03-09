import profile

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from app.EmailBackend import EmailBackend
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import CustomUser, Student
from webapp.forms import UserRegisterForm
from django.contrib.auth import get_user_model

# Create your views here.
class RegisterView(View):
    def get(self, request):
        return render(request, 'sign-up.html')
# New code to register using USER_TYPE

CustomUser = get_user_model()  # Get CustomUser model

def doRegister(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        user_type = request.POST.get("user_type")  # Get selected user role

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already taken!")
            return redirect('register')

        # Create user with correct user type
        user = CustomUser(username=username, email=email, user_type=user_type)
        user.set_password(password1)  # Hash password before saving
        user.save()
        
        login(request, user)  # Auto-login after registration
        return redirect("landing")

    return render(request, "sign-up.html")

def doLogin(request):
    if request.user.is_authenticated:
        messages.warning(request, "You're already logged in!")
        return redirect('landing')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get("password")

        # Authenticate user using email and password
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            user_type = user.user_type  # Get user role

            if user_type == '1':
                print("Logged in as HOD!")
                return redirect('hod_home')
            elif user_type == '2':
                print("Logged in as Staff!")
                return redirect('staff_home')
            elif user_type == '3':
                print("Logged in as Alumni!")
                return redirect('alumni_home')
            elif user_type == '4':
                print("Logged in as Student!")
                return redirect('landing')
            else:
                messages.error(request, 'Invalid user type!')
                return redirect('login')  
        else:
            messages.warning(request, "Invalid email or password!")

    return render(request, 'loginpage.html')
# -------------------------------------------------------------------------------------------
# Working code to register students     
# def registerStudents(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password1 = request.POST.get("password1")
#         password2 = request.POST.get("password2")

#         if password1 != password2:
#             messages.error(request, "Passwords do not match!")
#             return redirect('register')

#         if CustomUser.objects.filter(email=email).exists():
#             messages.error(request, "Email already taken!")
#             return redirect('register')

#         user = CustomUser(username=username, email=email, user_type='4')
#         user.set_password(password1)  # Hash password
#         user.save()
#         login(request, user)
#         return redirect("landing")

#     return render(request, "sign-up.html")
    # ---------------------------------------------------------------------------------------
# def doRegister(request):
#     if request.user.is_authenticated:
#         return redirect('landing')  # Redirect if already logged in

#     if request.method == "POST":
#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password1 = request.POST.get("password1")
#         password2 = request.POST.get("password2")

#         if password1 != password2:
#             return render(request, "sign-up.html", {"error": "Passwords do not match!"})

#         if CustomUser.objects.filter(username=username).exists():
#             return render(request, "sign-up.html", {"error": "Username already taken!"})

#         user = CustomUser.objects.create(username=username, email=email, password=password1)
#         user.user_type = '4'
#         user.save()
#         login(request, user)

#         return redirect('landing')
    
#     return render(request, 'sign-up.html')

# ----------------------------------------------------------------------------------------------------------------
# Last used login code before user_type code 

# def doLogin(request):
#     if request.user.is_authenticated:
#         messages.warning(request, "Hey, you're already logged in!")
#         print("Logged in already!")
#         return redirect('landing')

#     if request.method == "POST":
#         email = request.POST.get('email')
#         password = request.POST.get("password")

#         # Authenticate user
#         user = authenticate(request, username=email, password=password)

#         if user is not None:
#             login(request, user)
#             user_type = user.user_type  # Ensure it's a string

#             if user_type == '1':
#                 messages.success(request, f"Logged in {email} successfully!")
#                 return redirect('hod_home')
#             elif user_type == '2':
#                 messages.success(request, f"Logged in {email} successfully!")
#                 return redirect('staff_home')
#             elif user_type == '3':
#                 messages.success(request, f"Logged in {email} successfully!")
#                 return redirect('alumni_home')
#             elif user_type == '4':
#                 print('Student Logged In')
#                 messages.success(request, f"Logged in {email} successfully!")
#                 return redirect('landing')
#             else:
#                 print('Cannot login to the server')
#                 messages.error(request, 'Wrong Credentials, Try again!')
#                 return redirect('login')  
#         else:
#             print('User does not exist or incorrect password')
#             messages.warning(request, "Invalid email or password!")

#     return render(request, 'sign-in.html')


# def doLogin(request):

#     if request.user.is_authenticated:
#         messages.warning(request, f"Hey, you're already logged in!")
#         print("Logged in already!")
#         return redirect('landing')
    
#     if request.method == "POST":
#         email = request.POST.get('email') #user passed email
#         password = request.POST.get("password")

#         try:
#             user = CustomUser.objects.get(email=email)
#             #auto login user
#             user = authenticate(request, email=email, password=password, user_type='4')

#             if user is not None:
#                 login(request, user)
#                 user_type = user.user_type
#                 if user_type == '1':
#                     messages.success(request, f"Logged in {email} successfully!")
#                     return redirect('hod_home')
#                 elif user_type == '2':
#                     messages.success(request, f"Logged in {email} successfully!")
#                     return redirect('staff_home')
#                 elif user_type == '3':
#                     messages.success(request, f"Logged in {email} successfully!")
#                     return redirect('alumni_home')
#                 elif user_type == '4':
#                     print('Student Logged In')
#                     messages.success(request, f"Logged in {email} successfully!")
#                     return redirect('landing')
#                 else:
#                     print('Cannot login to the server')
#                     messages.error(request, 'Wrong Credentials, Try again!')
#                     return redirect('login')                
#             else:
#                 print('user does not exist')
#                 messages.warning(request, f"{email} Does Not Exist!")
#         except:
#             print('Login Unsuccessful!')
#             messages.warning(request, f"User with {email} doesn't exist!")

#     return render(request, 'sign-in.html')

def homeView(request):
    return render(request, 'hod/home.html')

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
@login_required(login_url='/login')
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