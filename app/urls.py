from django.urls import path
from . import views
from .views import IndexView, LoginView, DefaultView, RegisterView
from webapp.Public_Views import home_view

urlpatterns = [
    # Public home (replaces old userlanding.html for visitors)
    path('', home_view, name='landing'),
    path('index', IndexView.as_view(), name='index'),

    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('signup/', views.doRegister, name='doRegister'),
    path('login', LoginView.as_view(), name='login'),
    path('doLogin', views.doLogin, name='doLogin'),
    path('doLogout', views.doLogout, name='logout'),

    # Profile
    path('profile', views.profileView, name='profile'),
    path('profile/update', views.profileUpdate, name='profile_update'),
]
