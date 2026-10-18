from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from app.permissions import role_required
from django.contrib.auth.decorators import login_required
from app.models import SessionYear, Alumni, CustomUser, Staff, StaffNotification
from django.contrib import messages

@role_required('2')
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


@role_required('2')
def notification(request):
    notifications = StaffNotification.objects.filter(staff_id__admin=request.user)
    return render(request, 'Staff/notifications.html', {'notification': notifications})


@role_required('2')
@require_POST
def markAsDone(request, status):
    notification = get_object_or_404(StaffNotification, id=status, staff_id__admin=request.user)
    notification.status = 1
    notification.save()
    return redirect('notifications')