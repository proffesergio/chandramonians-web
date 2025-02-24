from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import SessionYear, Alumni, CustomUser, Staff, StaffNotification, ApplyForMembership, AlumniFeedback
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
    return render(request, 'hod/home.html', context)


@login_required(login_url='/')
def addAlumni(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        passing_year = request.POST.get('passing_year')
        phone = request.POST.get('phone')

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists!')
            return redirect('add_alumni')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning((request, 'Username already exists!'))
            return redirect('add_alumni')
        else:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                profile_pic=profile_pic,
                user_type=3,
            )
            if password != None and password != "":
                user.set_password(password)
            user.save()
            alumni = Alumni(
                admin=user,
                address=address,
                gender=gender,
                passing_year=passing_year,
                phone=phone,
            )
            alumni.save()
            messages.success(request,
                             user.first_name + " " + user.last_name + "'s " + "Alumni Record Saved Successfully!")
            return redirect('view_alumni')

            # session_year = SessionYear.objects.get(id = session_year_id)
    return render(request, 'hod/add_alumni.html')


def alumniView(request):
    alumni = Alumni.objects.all()

    context = {
        'alumni': alumni,
    }
    return render(request, 'hod/view_alumni.html', context)


def alumniEdit(request, id):
    alumni = Alumni.objects.filter(id=id)

    context = {
        'alumni': alumni
    }
    return render(request, 'hod/edit_alumni.html', context)


def alumniUpdate(request):
    if request.method == "POST":
        alumni_id = request.POST.get('alumni_id')

        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')

        user = CustomUser.objects.get(id=alumni_id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username

        if password != None and password != "":
            user.set_password(password)
        if profile_pic != None and profile_pic != "":
            user.profile_pic = profile_pic

        user.save()

        alumni = Alumni.objects.get(admin=alumni_id)
        alumni.address = address
        alumni.gender = gender

        alumni.save()
        messages.success(request, 'Record Updated Successfully!')

        return redirect('view_alumni')

    return render(request, 'hod/update_alumni.html')


def alumniDelete(request, admin):
    alumni = CustomUser.objects.get(id=admin)
    alumni.delete()
    messages.success(request, 'Record Deleted Successfully!')
    return redirect('view_alumni')

    return render(request, 'hod/delete_alumni.html')


def addStaff(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')


        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists!')
            return redirect('add_staff')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists!')
            return redirect('add_staff')
        else:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                profile_pic=profile_pic,
                user_type=2,
            )
            if password != None and password != "":
                user.set_password(password)
            user.save()
            staff = Staff(
                admin=user,
                address=address,
                gender=gender,
                phone=phone,
            )
            staff.save()
            messages.success(request,
                             user.first_name + " " + user.last_name + "'s " + "Staff Record Saved Successfully!")
            return redirect('view_staff')
    return render(request, 'hod/add_staff.html')


def viewStaff(request):
    staff = Staff.objects.all()

    context = {
        'staff': staff,
    }
    return render(request, 'hod/view_staff.html', context)


def editStaff(request, id):
    staff = Staff.objects.filter(id=id)

    context = {
        'staff': staff
    }
    return render(request, 'hod/edit_staff.html', context)


def deleteStaff(request, admin):
    staff = CustomUser.objects.get(id=admin)
    staff.delete()
    messages.success(request, 'Record Deleted Successfully!')
    return redirect('view_staff')

    return render(request, 'hod/delete_staff.html')


def updateStaff(request):
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')

        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')

        user = CustomUser.objects.get(id=staff_id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username

        if password != None and password != "":
            user.set_password(password)
        if profile_pic != None and profile_pic != "":
            user.profile_pic = profile_pic

        user.save()

        staff = Staff.objects.get(admin=staff_id)
        staff.address = address
        staff.gender = gender

        staff.save()
        messages.success(request, 'Record Updated Successfully!')

        return redirect('view_staff')

    return render(request, 'hod/update_staff.html')


def sendNotification(request):
    staff = Staff.objects.all()
    see_message = StaffNotification.objects.all()

    context = {
        'staff': staff,
        'see_message': see_message,
    }
    return render(request, 'hod/notify_staff.html', context)


def saveNotification(request):
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        message = request.POST.get('message')

        staff = Staff.objects.get(admin = staff_id)

        notification = StaffNotification(
            staff_id = staff,
            message = message,
        )
        notification.save()
        print('Saved Notification')
        messages.success(request, 'Notification saved successfully!')
        return redirect('notify_staff')
    return render(request, 'hod/notify_staff.html')


def membershipApplications(request):
    membership_apps = ApplyForMembership.objects.all()

    context = {
        'membership_apps': membership_apps,
    }
    return render(request, 'hod/membership_applications.html', context)


def membershipApproved(request, id):
    application = ApplyForMembership.objects.get(id = id)
    application.status = 1
    application.save()
    return redirect('membership_applications')


def membershipDenied(request, id):
    application = ApplyForMembership.objects.get(id=id)
    application.status = 2
    application.save()
    return redirect('membership_applications')


def alumFeedback(request):
    feedback = AlumniFeedback.objects.all()

    context = {
        'feedback': feedback,
    }
    return render(request, 'hod/alum_feedback.html', context)


def replyFeedback(request):
    if request.method == "POST":
        feedback_id = request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')

        print('Feedback ID: ', feedback_id)

        feedback = AlumniFeedback.objects.get(feedback_id)

        print('Feedback: ', feedback)

        feedback.feedback_reply = feedback_reply
        feedback.save()

        messages.success(request, 'Sent')

        return redirect('reply_feedback')
    else:
        messages.warning(request, 'Request Failed!')
        return redirect('alumni_feedback')

    return render(request, 'hod/reply_feedback.html')