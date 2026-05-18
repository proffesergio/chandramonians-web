import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from app.models import MembershipPayment, Alumni
from webapp.sheets_sync import sync_all


@login_required(login_url='/login')
def payment_records_view(request):
    """HOD only: full payment records table with sync controls."""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied.')
        return redirect('landing')

    member_type = request.GET.get('type', '')
    batch = request.GET.get('batch', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')

    qs = MembershipPayment.objects.all()
    if member_type:
        qs = qs.filter(member_type=member_type)
    if batch:
        qs = qs.filter(batch_year=batch)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(member_name__icontains=search)

    life_count = MembershipPayment.objects.filter(member_type='LIFE').count()
    general_count = MembershipPayment.objects.filter(member_type='GENERAL').count()
    batch_years = MembershipPayment.objects.values_list('batch_year', flat=True).distinct().exclude(batch_year='').order_by('batch_year')
    last_sync = MembershipPayment.objects.order_by('-last_synced_at').values_list('last_synced_at', flat=True).first()

    return render(request, 'members/payment_records.html', {
        'payments': qs,
        'life_count': life_count,
        'general_count': general_count,
        'batch_years': batch_years,
        'last_sync': last_sync,
        'filter_type': member_type,
        'filter_batch': batch,
        'filter_status': status,
        'search': search,
    })


@login_required(login_url='/login')
def trigger_sync_view(request):
    """HOD only: manually trigger Google Sheets sync."""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied.')
        return redirect('landing')

    result = sync_all()
    if result['success']:
        messages.success(
            request,
            f"Sync complete! Added: {result['total_added']}, "
            f"Updated: {result['total_updated']}, Errors: {result['total_errors']}"
        )
    else:
        messages.error(request, f"Sync failed: {result.get('error', 'Unknown error')}")

    return redirect('payment_records')


@login_required(login_url='/login')
def export_payments_csv(request):
    """HOD only: export payment records as CSV."""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied.')
        return redirect('landing')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="chandramonians_payments.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Type', 'Batch Year', 'Payment Date', 'Amount', 'Receipt No', 'Phone', 'Status'])

    for p in MembershipPayment.objects.all().order_by('member_type', 'member_name'):
        writer.writerow([
            p.member_name, p.get_member_type_display(), p.batch_year,
            p.payment_date or '', p.amount or '', p.receipt_number,
            p.phone, p.get_status_display(),
        ])

    return response


@login_required(login_url='/login')
def alumni_own_payment_view(request):
    """Alumni: view only their own payment record."""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied.')
        return redirect('landing')

    try:
        alumni = request.user.alumni
        full_name = f"{request.user.first_name} {request.user.last_name}".strip()
        payment = MembershipPayment.objects.filter(
            member_name__icontains=full_name.split()[0]
        ).first() if full_name else None
    except Exception:
        payment = None
        alumni = None

    return render(request, 'members/my_payment.html', {
        'payment': payment,
        'alumni': alumni,
    })


@login_required(login_url='/login')
def alumni_directory_view(request):
    """Full alumni directory for logged-in alumni."""
    batch = request.GET.get('batch', '')
    profession = request.GET.get('profession', '')
    search = request.GET.get('search', '')

    qs = Alumni.objects.select_related('admin').all()
    if batch:
        qs = qs.filter(passing_year=batch)
    if profession:
        qs = qs.filter(profession__icontains=profession)
    if search:
        qs = qs.filter(admin__first_name__icontains=search) | qs.filter(admin__last_name__icontains=search)

    batch_years = Alumni.objects.values_list('passing_year', flat=True).distinct().exclude(passing_year=None).order_by('passing_year')

    return render(request, 'members/directory.html', {
        'alumni': qs,
        'batch_years': batch_years,
        'filter_batch': batch,
        'search': search,
    })


@login_required(login_url='/login')
def job_board_view(request):
    """Placeholder: job board for alumni networking."""
    return render(request, 'members/job_board.html', {})


@login_required(login_url='/login')
def mentorship_view(request):
    """Alumni can sign up as mentors."""
    if request.method == 'POST':
        subject_area = request.POST.get('subject_area', '')
        availability = request.POST.get('availability', '')
        # TODO: Save to a Mentorship model (Phase 2 feature)
        messages.success(request, 'Thank you for signing up as a mentor! We will contact you soon.')
        return redirect('mentorship')
    return render(request, 'members/mentorship.html', {})
