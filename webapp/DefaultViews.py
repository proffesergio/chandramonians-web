from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import SessionYear, Alumni, CustomUser, Staff, StaffNotification
from django.contrib import messages

def defaultView(request):

    # dictionary to use on templates
    context = {
        
    }

    return render(request, 'landing.html', context)