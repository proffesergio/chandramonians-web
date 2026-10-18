from django.shortcuts import render, redirect, get_object_or_404
from app.permissions import role_required
from django.contrib.auth.decorators import login_required
from app.models import SessionYear, Alumni, CustomUser, Staff, StaffNotification, ApplyForMembership, AlumniFeedback, MembershipPayment
from django.contrib import messages
@role_required('3')
def applyForMembership(request):
    alumni = get_object_or_404(Alumni, admin=request.user)
    applications = ApplyForMembership.objects.filter(alum_id=alumni)
    return render(request, 'Alumni/membership_apply.html', {'logged_application': applications})

@role_required('3')
def homeView(request):
    alumni_count = Alumni.objects.all().count()
    staff_count = Staff.objects.all().count()
    user_count = CustomUser.objects.all().count()

    alumni_gender_male = Alumni.objects.filter(gender='Male').count()
    alumni_gender_female = Alumni.objects.filter(gender='Female').count()

    # Check if this alumni has a matching record in the member payment list
    membership_record = None
    full_name = f"{request.user.first_name} {request.user.last_name}".strip()
    if full_name:
        # Try exact name match first, then first-word match
        membership_record = (
            MembershipPayment.objects.filter(member_name__iexact=full_name).first()
            or MembershipPayment.objects.filter(
                member_name__icontains=request.user.first_name
            ).first() if request.user.first_name else None
        )

    context = {
        'alumni_count': alumni_count,
        'staff_count': staff_count,
        'user_count': user_count,
        'alumni_gender_male': alumni_gender_male,
        'alumni_gender_female': alumni_gender_female,
        'membership_record': membership_record,
    }
    return render(request, 'Alumni/alumni_home.html', context)

@role_required('3')
def saveApplication(request):
    if request.method == "POST":
        date = request.POST.get('date')
        note = request.POST.get('note')

        alumni = get_object_or_404(Alumni, admin=request.user)

        membership_apps = ApplyForMembership(
            alum_id = alumni,
            date = date,
            note = note
        )
        membership_apps.save()
        messages.success(request, 'Successfully Applied for Membership. Pending for approval!')

        return redirect('save_membership')

    return render(request, 'Alumni/save_membership.html')
@role_required('3')
def saveFeedback(request):
    if request.method == "POST":
        feedback = request.POST.get('feedback')

        alumni_feedback = get_object_or_404(Alumni, admin=request.user)

        feedback = AlumniFeedback(
            alum_id = alumni_feedback,
            feedback = feedback,
            feedback_reply = "",
        )
        feedback.save()
        messages.success(request, 'Successfully Sent your feedback. Thank you!')

        return redirect('alumni_feedback')

    return render(request, 'Alumni/save_feedback.html')


@role_required('3')
def alumniFeedback(request):
    alum_id = get_object_or_404(Alumni, admin=request.user)

    feedback_history = AlumniFeedback.objects.filter(alum_id = alum_id)

    context = {
        'feedback_history':feedback_history,
    }
    return render(request, 'Alumni/alumni_feedback.html', context)
