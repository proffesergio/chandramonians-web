from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from app.models import NewsArticle, Event, GalleryPhoto, Alumni, CommitteeMember, MembershipPayment


def health_check_view(request):
    return JsonResponse({'status': 'ok'})


def home_view(request):
    news = NewsArticle.objects.filter(is_published=True)[:6]
    events = Event.objects.filter(is_published=True).order_by('event_date')[:4]
    gallery = GalleryPhoto.objects.all()[:8]
    alumni_count = Alumni.objects.count()
    committee = CommitteeMember.objects.all()[:6]

    life_count = MembershipPayment.objects.filter(member_type='LIFE').count()
    general_count = MembershipPayment.objects.filter(member_type='GENERAL').count()
    total_raised = MembershipPayment.objects.filter(status='PAID').aggregate(
        total=Sum('amount')
    )['total'] or 0
    last_sync = MembershipPayment.objects.order_by('-last_synced_at').values_list(
        'last_synced_at', flat=True
    ).first()
    featured_members = MembershipPayment.objects.filter(
        status='PAID'
    ).order_by('member_name')[:18]

    context = {
        'news': news,
        'events': events,
        'gallery': gallery,
        'alumni_count': alumni_count,
        'committee': committee,
        'life_count': life_count,
        'general_count': general_count,
        'total_members': life_count + general_count,
        'total_raised': total_raised,
        'last_sync': last_sync,
        'featured_members': featured_members,
    }
    return render(request, 'public/home.html', context)


def about_view(request):
    committee = CommitteeMember.objects.all()
    context = {'committee': committee}
    return render(request, 'public/about.html', context)


def news_list_view(request):
    category = request.GET.get('category', '')
    qs = NewsArticle.objects.filter(is_published=True)
    if category:
        qs = qs.filter(category=category)
    context = {
        'articles': qs,
        'categories': NewsArticle.CATEGORY,
        'active_category': category,
    }
    return render(request, 'public/news_list.html', context)


def news_detail_view(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    related = NewsArticle.objects.filter(
        is_published=True, category=article.category
    ).exclude(pk=article.pk)[:3]
    return render(request, 'public/news_detail.html', {'article': article, 'related': related})


def events_view(request):
    from django.utils import timezone
    upcoming = Event.objects.filter(is_published=True, event_date__gte=timezone.now()).order_by('event_date')
    past = Event.objects.filter(is_published=True, event_date__lt=timezone.now()).order_by('-event_date')[:6]
    return render(request, 'public/events.html', {'upcoming': upcoming, 'past': past})


def gallery_view(request):
    category = request.GET.get('category', '')
    qs = GalleryPhoto.objects.all()
    if category:
        qs = qs.filter(category=category)
    categories = GalleryPhoto.objects.values_list('category', flat=True).distinct().exclude(category='')
    return render(request, 'public/gallery.html', {
        'photos': qs,
        'categories': categories,
        'active_category': category,
    })


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            try:
                send_mail(
                    subject=f"[Chandramonians Contact] {subject}",
                    message=f"From: {name} <{email}>\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent! We will get back to you soon.')
            except Exception:
                messages.error(request, 'Message could not be sent. Please try again or contact us directly.')
        else:
            messages.error(request, 'Please fill in all required fields.')

        return redirect('contact')

    return render(request, 'public/contact.html')


def alumni_public_directory_view(request):
    batch = request.GET.get('batch', '')
    alumni = Alumni.objects.select_related('admin').all()
    if batch:
        alumni = alumni.filter(passing_year=batch)
    batch_years = Alumni.objects.values_list('passing_year', flat=True).distinct().exclude(passing_year=None).order_by('passing_year')
    return render(request, 'public/alumni_directory.html', {
        'alumni': alumni,
        'batch_years': batch_years,
        'active_batch': batch,
    })


def public_members_view(request):
    """Public: membership directory split into Life / General tabs."""
    batch = request.GET.get('batch', '')
    status = request.GET.get('status', '')
    search = request.GET.get('q', '')

    qs = MembershipPayment.objects.all()
    if batch:
        qs = qs.filter(batch_year=batch)
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(member_name__icontains=search)

    life_members = qs.filter(member_type='LIFE')
    general_members = qs.filter(member_type='GENERAL')

    batch_years = MembershipPayment.objects.values_list(
        'batch_year', flat=True
    ).distinct().exclude(batch_year='').order_by('batch_year')
    life_count = MembershipPayment.objects.filter(member_type='LIFE').count()
    general_count = MembershipPayment.objects.filter(member_type='GENERAL').count()
    last_sync = MembershipPayment.objects.order_by('-last_synced_at').values_list(
        'last_synced_at', flat=True
    ).first()

    return render(request, 'public/members.html', {
        'life_members': life_members,
        'general_members': general_members,
        'batch_years': batch_years,
        'life_count': life_count,
        'general_count': general_count,
        'total': life_count + general_count,
        'last_sync': last_sync,
        'filter_batch': batch,
        'filter_status': status,
        'search': search,
    })
