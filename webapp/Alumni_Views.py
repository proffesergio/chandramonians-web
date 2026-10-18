from django.shortcuts import render, redirect, get_object_or_404
from app.permissions import role_required
from app.models import Alumni, ApplyForMembership, AlumniFeedback
from app.forms import MembershipApplicationForm
from webapp.Member_Views import resolve_membership_record
from django.contrib import messages
@role_required('3')
def applyForMembership(request):
    alumni = get_object_or_404(Alumni, admin=request.user)
    applications = ApplyForMembership.objects.filter(alum_id=alumni).order_by('-created_at')
    form = MembershipApplicationForm()
    return render(request, 'Alumni/membership_apply.html', {'logged_application': applications, 'form': form})

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
    if request.method != 'POST':
        return redirect('membership_apply')
    alumni = get_object_or_404(Alumni, admin=request.user)
    form = MembershipApplicationForm(request.POST)
    membership_type = request.POST.get('membership_type', '')
    if form.is_valid():
        if ApplyForMembership.objects.filter(alum_id=alumni, membership_type=membership_type, status=0).exists():
            form.add_error(None, 'You already have a pending application for this membership type.')
        else:
            application = form.save(commit=False)
            application.alum_id = alumni
            application.save()
            messages.success(request, f'{application.get_membership_type_display()} application submitted for review.')
            return redirect('membership_apply')
    applications = ApplyForMembership.objects.filter(alum_id=alumni).order_by('-created_at')
    return render(request, 'Alumni/membership_apply.html', {'logged_application': applications, 'form': form})
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
