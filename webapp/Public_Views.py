import urllib.request
import xml.etree.ElementTree as ET
import logging
import os

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from django.core.cache import cache
from app.models import NewsArticle, Event, GalleryPhoto, Alumni, CommitteeMember, MembershipPayment, VolunteerApplication
from app.forms import VolunteerApplicationForm
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_safe
from django.http import HttpResponse, HttpResponseNotModified
from app.models import ProfilePicture
from app.map_data import countries, country_choices
from django.db.models import Count
from datetime import timedelta

logger = logging.getLogger(__name__)

RSS_SOURCES = [
    ('The Daily Star', 'https://www.thedailystar.net/frontpage/rss.xml'),
    ('Prothom Alo Eng', 'https://en.prothomalo.com/rss.xml'),
]


def _fetch_rss_headlines():
    """Fetch up to 6 headlines per source. Cached for 1 hour. Returns list of dicts."""
    cached = cache.get('bd_news_headlines')
    if cached is not None:
        return cached
    items = []
    for source, url in RSS_SOURCES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                root = ET.fromstring(resp.read())
            count = 0
            for item in root.iter('item'):
                title = (item.findtext('title') or '').strip()
                link = (item.findtext('link') or '').strip()
                pub = (item.findtext('pubDate') or '').strip()
                if title and link:
                    items.append({'source': source, 'title': title, 'link': link, 'pub': pub})
                    count += 1
                    if count >= 6:
                        break
        except Exception as exc:
            logger.warning("RSS fetch failed for %s: %s", source, exc)
    cache.set('bd_news_headlines', items, 3600)
    return items


def health_check_view(request):
    response = JsonResponse({'status': 'ok', 'revision': os.environ.get('VERCEL_GIT_COMMIT_SHA', '')})
    response['Cache-Control'] = 'no-store'
    return response


@require_safe
def profile_picture_view(request, picture_id):
    picture = get_object_or_404(ProfilePicture, pk=picture_id)
    etag = f'"{picture_id}"'
    if request.headers.get('If-None-Match') == etag:
        response = HttpResponseNotModified()
    else:
        response = HttpResponse(bytes(picture.content), content_type='image/webp')
        response['X-Content-Type-Options'] = 'nosniff'
    response['ETag'] = etag
    response['Cache-Control'] = 'public, max-age=86400, immutable'
    return response


@require_safe
def alumni_map_view(request):
    all_alumni = Alumni.objects.select_related('admin').filter(admin__is_active=True, admin__user_type='3')
    alumni = all_alumni
    query = request.GET.get('q', '').strip()
    batch = request.GET.get('batch', '').strip()
    country = request.GET.get('country', '').strip()
    if query:
        alumni = alumni.filter(Q(admin__first_name__icontains=query) | Q(admin__last_name__icontains=query) |
                               Q(admin__username__icontains=query) | Q(profession__icontains=query))
    if batch:
        alumni = alumni.filter(passing_year=batch)
    shared = alumni.filter(map_visible=True, map_country__in=countries())
    markers = []
    for row in shared.values('map_country').annotate(count=Count('id')):
        markers.append(dict(countries()[row['map_country']], code=row['map_country'], count=row['count']))
    if country:
        alumni = alumni.filter(map_visible=True, map_country=country) if country in countries() else alumni.none()
    return render(request, 'pages/alumni_map.html', {
        'alumni_list': alumni.order_by('admin__first_name', 'admin__last_name', 'pk'),
        'registered_count': all_alumni.count(), 'shared_count': shared.count(),
        'markers': sorted(markers, key=lambda row: row['name']), 'countries': country_choices()[1:],
        'batch_years': all_alumni.exclude(passing_year__isnull=True).exclude(passing_year='').values_list('passing_year', flat=True).distinct().order_by('passing_year'),
        'filter_country': country, 'filter_batch': batch, 'search': query,
    })


def home_view(request):
    news = NewsArticle.objects.filter(is_published=True)[:6]
    events = Event.objects.filter(is_published=True, status='SCHEDULED', event_date__gte=timezone.now()).order_by('event_date')[:3]
    alumni_count = Alumni.objects.count()

    life_count = MembershipPayment.objects.filter(member_type='LIFE').count()
    general_count = MembershipPayment.objects.filter(member_type='GENERAL').count()
    featured_members = MembershipPayment.objects.all().order_by('member_name')[:8]
    completed = Event.objects.filter(is_published=True, status='COMPLETED')

    context = {
        'news': news,
        'events': events,
        'alumni_count': alumni_count,
        'mapped_alumni_count': Alumni.objects.filter(admin__is_active=True, admin__user_type='3', map_visible=True, map_country__in=countries()).count(),
        'life_count': life_count,
        'general_count': general_count,
        'total_members': life_count + general_count,
        'featured_members': featured_members,
        'completed_activities': completed.count(),
        'recent_outcomes': completed.exclude(outcome='').order_by('-event_date')[:3],
        'upcoming_count': Event.objects.filter(is_published=True, status='SCHEDULED', event_date__gte=timezone.now()).count(),
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    from app.models import Staff, Event
    committee = CommitteeMember.objects.all()
    alumni_count = Alumni.objects.count()
    staff_count = Staff.objects.count()
    events_count = Event.objects.count()
    total_members = MembershipPayment.objects.count()
    context = {
        'committee': committee,
        'alumni_count': alumni_count,
        'staff_count': staff_count,
        'events_count': events_count,
        'total_members': total_members,
    }
    return render(request, 'pages/about.html', context)


def news_list_view(request):
    category = request.GET.get('category', '')
    qs = NewsArticle.objects.filter(is_published=True)
    if category:
        qs = qs.filter(category=category)
    external_news = _fetch_rss_headlines()
    context = {
        'articles': qs,
        'categories': NewsArticle.CATEGORY,
        'active_category': category,
        'external_news': external_news,
    }
    return render(request, 'pages/news_list.html', context)


def news_detail_view(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    related = NewsArticle.objects.filter(
        is_published=True, category=article.category
    ).exclude(pk=article.pk)[:3]
    return render(request, 'pages/news_detail.html', {'article': article, 'related': related})


def events_view(request):
    from django.utils import timezone
    qs = Event.objects.filter(is_published=True).exclude(status='CANCELLED')
    kind = request.GET.get('type', '')
    if kind in dict(Event.ACTIVITY_TYPES):
        qs = qs.filter(activity_type=kind)
    upcoming = qs.filter(event_date__gte=timezone.now(), status='SCHEDULED').order_by('event_date')
    past = qs.filter(Q(event_date__lt=timezone.now()) | Q(status='COMPLETED')).order_by('-event_date')[:12]
    return render(request, 'pages/events.html', {
        'upcoming_events': upcoming, 'past_events': past,
        'activity_types': Event.ACTIVITY_TYPES, 'active_type': kind,
    })


@require_http_methods(['GET', 'POST'])
def volunteer_view(request):
    initial = {'interest': request.GET.get('interest', 'GUEST_CLASS')}
    form = VolunteerApplicationForm(request.POST if request.method == 'POST' else None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        contact = Q()
        if form.cleaned_data.get('email'):
            contact |= Q(email__iexact=form.cleaned_data['email'])
        if form.cleaned_data.get('phone'):
            contact |= Q(phone=form.cleaned_data['phone'])
        recent = VolunteerApplication.objects.filter(contact, created_at__gte=timezone.now() - timedelta(minutes=10)).exists()
        if recent:
            form.add_error(None, 'An application with this contact information was received recently. Please give the team time to review it.')
        else:
            form.save()
            return redirect('volunteer_received')
    return render(request, 'pages/volunteer.html', {'form': form})


def volunteer_received_view(request):
    return render(request, 'pages/volunteer_received.html')


def gallery_view(request):
    category = request.GET.get('category', '')
    qs = GalleryPhoto.objects.all()
    if category:
        qs = qs.filter(category=category)
    categories = GalleryPhoto.objects.values_list('category', flat=True).distinct().exclude(category='')
    return render(request, 'pages/gallery.html', {
        'photos': qs,
        'categories': categories,
        'active_category': category,
    })


def contact_view(request):
    from app.forms import ContactForm

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                EmailMessage(
                    subject=f"[Chandramonians Contact] {subject}",
                    body=f"From: {name} <{email}>\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ADMIN_EMAIL],
                    reply_to=[email],
                ).send(fail_silently=False)
                messages.success(request, 'Your message has been sent! We will get back to you soon.')
            except Exception:
                messages.error(request, 'Message could not be sent. Please try again or contact us directly.')
        else:
            messages.error(request, 'Please enter a valid email address and complete the required fields within their length limits.')

        return redirect('contact')

    return render(request, 'pages/contact.html', {'admin_email': settings.ADMIN_EMAIL})


def alumni_public_directory_view(request):
    batch = request.GET.get('batch', '')
    search = request.GET.get('q', '').strip()
    alumni = Alumni.objects.select_related('admin').all()
    if batch:
        alumni = alumni.filter(passing_year=batch)
    if search:
        alumni = alumni.filter(Q(admin__first_name__icontains=search) | Q(admin__last_name__icontains=search))
    batch_years = Alumni.objects.values_list('passing_year', flat=True).distinct().exclude(passing_year=None).order_by('passing_year')
    return render(request, 'pages/alumni_directory.html', {
        'alumni_list': alumni,
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

    return render(request, 'pages/members.html', {
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
