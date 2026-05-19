from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from . import views, Hod_Views, Staff_Views, Alumni_Views
from . import Public_Views, Education_Views, Member_Views

urlpatterns = [
    path('health/', Public_Views.health_check_view, name='health_check'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('app.urls')),

    # ── Public Pages ─────────────────────────────────────────────────────────
    path('about/', Public_Views.about_view, name='about'),
    path('news/', Public_Views.news_list_view, name='news_list'),
    path('news/<slug:slug>/', Public_Views.news_detail_view, name='news_detail'),
    path('events/', Public_Views.events_view, name='events'),
    path('gallery/', Public_Views.gallery_view, name='gallery'),
    path('contact/', Public_Views.contact_view, name='contact'),
    path('directory/', Public_Views.alumni_public_directory_view, name='public_directory'),
    path('members/', Public_Views.public_members_view, name='public_members'),

    # ── HOD Panel ─────────────────────────────────────────────────────────────
    path('hod/home', Hod_Views.homeView, name='hod_home'),
    path('hod/alumni/add', Hod_Views.addAlumni, name='add_alumni'),
    path('hod/alumni/view', Hod_Views.alumniView, name='view_alumni'),
    path('hod/alumni/edit/<str:id>', Hod_Views.alumniEdit, name='edit_alumni'),
    path('hod/alumni/update', Hod_Views.alumniUpdate, name='update_alumni'),
    path('hod/alumni/delete/<str:admin>', Hod_Views.alumniDelete, name='delete_alumni'),
    path('hod/staff/add', Hod_Views.addStaff, name='add_staff'),
    path('hod/staff/view', Hod_Views.viewStaff, name='view_staff'),
    path('hod/staff/edit/<str:id>', Hod_Views.editStaff, name='edit_staff'),
    path('hod/staff/update', Hod_Views.updateStaff, name='update_staff'),
    path('hod/staff/delete/<str:admin>', Hod_Views.deleteStaff, name='delete_staff'),
    path('hod/staff/notify', Hod_Views.sendNotification, name='notify_staff'),
    path('hod/staff/save', Hod_Views.saveNotification, name='save_notification'),
    path('hod/alumni/membership_applications', Hod_Views.membershipApplications, name='membership_applications'),
    path('hod/alumni/membership_approval/<str:id>', Hod_Views.membershipApproved, name='membership_approved'),
    path('hod/alumni/membership_denial/<str:id>', Hod_Views.membershipDenied, name='membership_denied'),
    path('hod/alumni/feedback', Hod_Views.alumFeedback, name='alum_feedback'),
    path('hod/alumni/reply_feedback', Hod_Views.replyFeedback, name='reply_feedback'),

    # ── HOD Payment Records ───────────────────────────────────────────────────
    path('hod/payments/', Member_Views.payment_records_view, name='payment_records'),
    path('hod/payments/sync/', Member_Views.trigger_sync_view, name='trigger_sync'),
    path('hod/payments/export/', Member_Views.export_payments_csv, name='export_payments'),
    path('hod/payments/upload/csv/', Member_Views.upload_payments_csv_view, name='upload_payments_csv'),
    path('hod/payments/upload/excel/', Member_Views.upload_payments_excel_view, name='upload_payments_excel'),

    # ── Staff Panel ───────────────────────────────────────────────────────────
    path('Staff/home', Staff_Views.homeView, name='staff_home'),
    path('Staff/Notification', Staff_Views.notification, name='notifications'),
    path('Staff/mark_as_done/<str:status>', Staff_Views.markAsDone, name='mark_as_done'),

    # ── Alumni Portal ─────────────────────────────────────────────────────────
    path('Alumni/Home', Alumni_Views.homeView, name='alumni_home'),
    path('Alumni/ApplyForMembership', Alumni_Views.applyForMembership, name='membership_apply'),
    path('Alumni/SendApplication', Alumni_Views.saveApplication, name='save_membership'),
    path('Alumni/Feedback', Alumni_Views.alumniFeedback, name='alumni_feedback'),
    path('Alumni/SendFeedback', Alumni_Views.saveFeedback, name='save_feedback'),
    path('Alumni/Payments/', Member_Views.alumni_own_payment_view, name='alumni_payments'),
    path('Alumni/Directory/', Member_Views.alumni_directory_view, name='alumni_directory'),
    path('Alumni/Jobs/', Member_Views.job_board_view, name='job_board'),
    path('Alumni/Mentorship/', Member_Views.mentorship_view, name='mentorship'),

    # ── Student Educational Hub ───────────────────────────────────────────────
    path('edu/', Education_Views.edu_home_view, name='edu_home'),
    path('edu/tutor/', Education_Views.ai_tutor_view, name='ai_tutor'),
    path('edu/tutor/ask/', Education_Views.ai_tutor_ask, name='ai_tutor_ask'),
    path('edu/challenge/', Education_Views.daily_challenge_view, name='daily_challenge'),
    path('edu/challenge/submit/', Education_Views.submit_challenge, name='submit_challenge'),
    path('edu/suggestions/', Education_Views.suggestions_view, name='suggestions'),
    path('edu/suggestions/<int:pk>/', Education_Views.suggestion_detail_view, name='suggestion_detail'),
    path('edu/leaderboard/', Education_Views.leaderboard_view, name='leaderboard'),
    path('edu/newspapers/', Education_Views.newspapers_view, name='newspapers'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
