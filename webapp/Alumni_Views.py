from django.shortcuts import render, redirect, get_object_or_404
from app.permissions import role_required
from app.models import Alumni, ApplyForMembership, AlumniFeedback
from webapp.Member_Views import resolve_membership_record
from django.contrib import messages
@role_required('3')
def applyForMembership(request):
    alumni = get_object_or_404(Alumni, admin=request.user)
    applications = ApplyForMembership.objects.filter(alum_id=alumni)
    return render(request, 'Alumni/membership_apply.html', {'logged_application': applications})

@role_required('3')
def homeView(request):
    alumni = get_object_or_404(Alumni, admin=request.user)
    membership_record = resolve_membership_record(request.user, alumni)
    applications = ApplyForMembership.objects.filter(alum_id=alumni)
    feedback_count = AlumniFeedback.objects.filter(alum_id=alumni).count()
    profile_fields = (request.user.first_name, request.user.last_name, alumni.phone,
                      alumni.passing_year, alumni.profession, alumni.company, alumni.bio)
    profile_completion = round(sum(bool(value) for value in profile_fields) / len(profile_fields) * 100)

    context = {
        'alumni': alumni,
        'membership_record': membership_record,
        'application_count': applications.count(),
        'approved_application_count': applications.filter(status=1).count(),
        'feedback_count': feedback_count,
        'profile_completion': profile_completion,
        'map_shared': bool(alumni.map_visible and alumni.map_country),
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
