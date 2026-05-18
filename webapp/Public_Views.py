from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from app.models import NewsArticle, Event, GalleryPhoto, Alumni, CommitteeMember


def health_check_view(request):
    return JsonResponse({'status': 'ok'})


def home_view(request):
    news = NewsArticle.objects.filter(is_published=True)[:6]
    events = Event.objects.filter(is_published=True).order_by('event_date')[:4]
    gallery = GalleryPhoto.objects.all()[:8]
    alumni_count = Alumni.objects.count()
    committee = CommitteeMember.objects.all()[:6]

    context = {
        'news': news,
        'events': events,
        'gallery': gallery,
        'alumni_count': alumni_count,
        'committee': committee,
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
