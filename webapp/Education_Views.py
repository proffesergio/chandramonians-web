import uuid
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django_htmx.http import HttpResponseClientRedirect

from app.models import (
    ExamSuggestion, Subject, DailyChallenge, StudentProgress, AIChat,
)


def _get_or_create_progress(user):
    progress, _ = StudentProgress.objects.get_or_create(user=user)
    return progress


def _update_streak(progress):
    today = date.today()
    if progress.last_active_date == today:
        return
    if progress.last_active_date == today - timedelta(days=1):
        progress.current_streak += 1
    else:
        progress.current_streak = 1
    progress.longest_streak = max(progress.longest_streak, progress.current_streak)
    progress.last_active_date = today
    progress.total_xp += 2  # daily login XP
    progress.save()


@login_required(login_url='/login')
def edu_home_view(request):
    progress = _get_or_create_progress(request.user)
    _update_streak(progress)

    today_challenge = DailyChallenge.objects.filter(date=date.today()).first()
    recent_suggestions = ExamSuggestion.objects.filter(is_published=True).select_related('subject')[:5]

    # Leaderboard snapshot (top 5)
    leaderboard = StudentProgress.objects.select_related('user').order_by('-total_xp')[:5]

    # Newspaper links (curated, static list — update as needed)
    newspapers = [
        {'name': 'Prothom Alo', 'url': 'https://www.prothomalo.com', 'lang': 'Bengali', 'icon': '📰'},
        {'name': 'The Daily Star', 'url': 'https://www.thedailystar.net', 'lang': 'English', 'icon': '⭐'},
        {'name': 'Samakal', 'url': 'https://samakal.com', 'lang': 'Bengali', 'icon': '📄'},
        {'name': 'Jugantor', 'url': 'https://www.jugantor.com', 'lang': 'Bengali', 'icon': '📋'},
        {'name': 'Kaler Kantho', 'url': 'https://www.kalerkantho.com', 'lang': 'Bengali', 'icon': '🗞️'},
        {'name': 'The Business Standard', 'url': 'https://www.tbsnews.net', 'lang': 'English', 'icon': '💼'},
    ]

    context = {
        'progress': progress,
        'today_challenge': today_challenge,
        'recent_suggestions': recent_suggestions,
        'leaderboard': leaderboard,
        'newspapers': newspapers,
    }
    return render(request, 'education/hub.html', context)


@login_required(login_url='/login')
def ai_tutor_view(request):
    progress = _get_or_create_progress(request.user)
    subjects = Subject.objects.all()
    # Load last 10 chat messages for this session
    session_id = request.session.get('ai_session_id', str(uuid.uuid4()))
    request.session['ai_session_id'] = session_id
    chat_history = AIChat.objects.filter(session_id=session_id).order_by('created_at')[:20]
    return render(request, 'education/ai_tutor.html', {
        'subjects': subjects,
        'chat_history': chat_history,
        'progress': progress,
    })


@login_required(login_url='/login')
@require_POST
def ai_tutor_ask(request):
    """HTMX endpoint: receives question, returns HTML chat bubble fragment."""
    from webapp.ai_service import get_tutoring_response

    question = request.POST.get('question', '').strip()
    subject = request.POST.get('subject', '').strip()

    if not question:
        return render(request, 'education/partials/chat_error.html', {'error': 'Please enter a question.'})

    session_id = request.session.get('ai_session_id', str(uuid.uuid4()))
    request.session['ai_session_id'] = session_id

    answer = get_tutoring_response(question, subject=subject)

    AIChat.objects.create(
        user=request.user,
        session_id=session_id,
        question=question,
        answer=answer,
        subject=subject,
    )

    progress = _get_or_create_progress(request.user)
    progress.ai_queries_used += 1
    progress.total_xp += 1
    progress.save()

    return render(request, 'education/partials/chat_bubble.html', {
        'question': question,
        'answer': answer,
    })


@login_required(login_url='/login')
def daily_challenge_view(request):
    today = date.today()
    challenge = DailyChallenge.objects.filter(date=today).first()
    progress = _get_or_create_progress(request.user)

    already_done = request.session.get(f'challenge_done_{today}', False)

    return render(request, 'education/challenge.html', {
        'challenge': challenge,
        'progress': progress,
        'already_done': already_done,
    })


@login_required(login_url='/login')
@require_POST
def submit_challenge(request):
    today = date.today()
    challenge = get_object_or_404(DailyChallenge, date=today)

    if request.session.get(f'challenge_done_{today}', False):
        return render(request, 'education/partials/challenge_result.html', {
            'already_done': True,
        })

    selected = request.POST.get('answer', '').lower().strip()
    is_correct = selected == challenge.correct_option.lower()

    progress = _get_or_create_progress(request.user)
    xp_earned = 0

    if is_correct:
        xp_earned = 10
        if progress.current_streak > 0 and progress.current_streak % 7 == 0:
            xp_earned += 20  # streak bonus
        progress.total_xp += xp_earned
        progress.challenges_completed += 1
        progress.save()

    request.session[f'challenge_done_{today}'] = True

    return render(request, 'education/partials/challenge_result.html', {
        'is_correct': is_correct,
        'selected': selected,
        'correct': challenge.correct_option,
        'explanation': challenge.explanation,
        'xp_earned': xp_earned,
        'progress': progress,
    })


@login_required(login_url='/login')
def suggestions_view(request):
    grade = request.GET.get('grade', '')
    subject_id = request.GET.get('subject', '')

    qs = ExamSuggestion.objects.filter(is_published=True).select_related('subject')
    if grade:
        qs = qs.filter(subject__grade=grade)
    if subject_id:
        qs = qs.filter(subject_id=subject_id)

    subjects = Subject.objects.all()
    grades = Subject.GRADE_CHOICES

    return render(request, 'education/suggestions.html', {
        'suggestions': qs,
        'subjects': subjects,
        'grades': grades,
        'active_grade': grade,
        'active_subject': subject_id,
    })


@login_required(login_url='/login')
def suggestion_detail_view(request, pk):
    suggestion = get_object_or_404(ExamSuggestion, pk=pk, is_published=True)
    return render(request, 'education/suggestion_detail.html', {'suggestion': suggestion})


@login_required(login_url='/login')
def leaderboard_view(request):
    from django.db.models import F
    from datetime import timedelta

    week_ago = date.today() - timedelta(days=7)
    top_students = StudentProgress.objects.select_related('user').order_by('-total_xp')[:20]
    progress = _get_or_create_progress(request.user)

    return render(request, 'education/leaderboard.html', {
        'top_students': top_students,
        'my_progress': progress,
    })


@login_required(login_url='/login')
def newspapers_view(request):
    newspapers = [
        {'name': 'Prothom Alo', 'url': 'https://www.prothomalo.com', 'lang': 'Bengali', 'desc': 'Leading Bengali daily'},
        {'name': 'The Daily Star', 'url': 'https://www.thedailystar.net', 'lang': 'English', 'desc': 'Leading English daily'},
        {'name': 'Samakal', 'url': 'https://samakal.com', 'lang': 'Bengali', 'desc': 'Popular Bengali daily'},
        {'name': 'Jugantor', 'url': 'https://www.jugantor.com', 'lang': 'Bengali', 'desc': 'Bengali news daily'},
        {'name': 'Kaler Kantho', 'url': 'https://www.kalerkantho.com', 'lang': 'Bengali', 'desc': 'Bengali daily'},
        {'name': 'The Business Standard', 'url': 'https://www.tbsnews.net', 'lang': 'English', 'desc': 'Business & general news'},
        {'name': 'Dhaka Tribune', 'url': 'https://www.dhakatribune.com', 'lang': 'English', 'desc': 'English daily'},
        {'name': 'Ittefaq', 'url': 'https://www.ittefaq.com.bd', 'lang': 'Bengali', 'desc': 'Historic Bengali daily'},
    ]
    education_links = [
        {'name': 'Dinajpur Education Board', 'url': 'https://dinajpureducationboard.gov.bd', 'desc': 'Official notices & results'},
        {'name': 'DSHE (Directorate)', 'url': 'https://dshe.gov.bd', 'desc': 'Secondary & higher education notices'},
        {'name': 'Bangladesh Education Board Results', 'url': 'https://eboardresults.com', 'desc': 'Check SSC/HSC results'},
        {'name': '10 Minute School', 'url': 'https://10minuteschool.com', 'desc': 'Free video lessons'},
    ]
    return render(request, 'education/newspapers.html', {
        'newspapers': newspapers,
        'education_links': education_links,
    })
