from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import SessionYear, Alumni, CustomUser, Staff, StaffNotification, ApplyForMembership, AlumniFeedback
from django.contrib import messages
@login_required(login_url='/')
def applyForMembership(request):
    # get logged in user
    alumni = Alumni.objects.filter(admin = request.user.id)
    for i in alumni:
        alum_id = i.id
        print('Current logged in user:', alum_id, ' ', i.admin.first_name)

        logged_application = ApplyForMembership.objects.filter(alum_id = alum_id)

        context = {
            'logged_application':logged_application,
        }

        return render(request, 'Alumni/membership_apply.html', context)

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
    return render(request, 'Alumni/alumni_home.html', context)

@login_required(login_url='/')
def saveApplication(request):
    if request.method == "POST":
        date = request.POST.get('date')
        note = request.POST.get('note')

        alumni = Alumni.objects.get(admin = request.user.id)

        membership_apps = ApplyForMembership(
            alum_id = alumni,
            date = date,
            note = note
        )
        membership_apps.save()
        messages.success(request, 'Successfully Applied for Membership. Pending for approval!')

        return redirect('save_membership')

    return render(request, 'Alumni/save_membership.html')
@login_required(login_url='/')
def saveFeedback(request):
    if request.method == "POST":
        feedback = request.POST.get('feedback')

        alumni_feedback = Alumni.objects.get(admin = request.user.id)

        feedback = AlumniFeedback(
            alum_id = alumni_feedback,
            feedback = feedback,
            feedback_reply = "",
        )
        feedback.save()
        messages.success(request, 'Successfully Sent your feedback. Thank you!')

        return redirect('alumni_feedback')

    return render(request, 'Alumni/save_feedback.html')


def alumniFeedback(request):
    alum_id = Alumni.objects.get(admin = request.user.id)

    feedback_history = AlumniFeedback.objects.filter(alum_id = alum_id)

    context = {
        'feedback_history':feedback_history,
    }
    return render(request, 'Alumni/alumni_feedback.html', context)