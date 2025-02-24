from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import SessionYear, Alumni, CustomUser, Staff, StaffNotification
from django.contrib import messages

@login_required(login_url='/')
def homeView(request):
    alumni_count = Alumni.objects.all().count()
    staff_count = Staff.objects.all().count()
    user_count = CustomUser.objects.all().count()

    alumni_gender_male = Alumni.objects.filter(gender='Male').count()
    alumni_gender_female = Alumni.objects.filter(gender='Female').count()

    # dictionary to use on templates
    context = {
        'alumni_count': alumni_count,
        'staff_count': staff_count,
        'user_count': user_count,
        'alumni_gender_male': alumni_gender_male,
        'alumni_gender_female': alumni_gender_female,
    }
    return render(request, 'Staff/staff_home.html', context)


def notification(request):
    staff = Staff.objects.filter(admin = request.user.id)
    for i in staff:
        print(i.id)
        staff_id = i.id

        notification = StaffNotification.objects.filter(staff_id = staff_id)

        context = {
            'notification': notification,
        }
        return render(request, 'Staff/notifications.html', context)


def markAsDone(request, status):
    notification = StaffNotification.objects.get(id = status)
    notification.status = 1
    notification.save()
    return redirect('notifications')