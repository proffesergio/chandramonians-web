from django.urls import path
from . import views
from .views import IndexView, LoginView

urlpatterns = [
    path('index', IndexView.as_view(), name = "index"),
    #Login Path
    path('', LoginView.as_view(), name = "login"),
    path('doLogin', views.doLogin, name = "doLogin"),
    path('doLogout', views.doLogout, name = "logout"),

    # Profile Path
    path('profile', views.profileView, name = "profile"),
    path('profile/update', views.profileUpdate, name = "profile_update"),



    #HOD Path
    # path('hod/home', views.homeView, name = "hod_home"),

    # path('', views.index, name="index"),
    # path('', views.add_alumni, name="alumni"),
]