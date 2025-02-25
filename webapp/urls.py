from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views, Hod_Views, Staff_Views, Alumni_Views

urlpatterns = [
    # adding the app to the main path
    path('admin/', admin.site.urls),
    path('', include('app.urls')),

    # hod Path
    path('hod/home', Hod_Views.homeView, name="hod_home"),
    path('hod/alumni/add', Hod_Views.addAlumni, name="add_alumni"),
    path('hod/alumni/view', Hod_Views.alumniView, name="view_alumni"),
    path('hod/alumni/edit/<str:id>', Hod_Views.alumniEdit, name="edit_alumni"),
    path('hod/alumni/update', Hod_Views.alumniUpdate, name="update_alumni"),
    path('hod/alumni/delete/<str:admin>', Hod_Views.alumniDelete, name="delete_alumni"),

    # HOD Staff Path
    path('hod/staff/add', Hod_Views.addStaff, name="add_staff"),
    path('hod/staff/view', Hod_Views.viewStaff, name="view_staff"),
    path('hod/staff/edit/<str:id>', Hod_Views.editStaff, name="edit_staff"),
    path('hod/staff/update', Hod_Views.updateStaff, name="update_staff"),
    path('hod/staff/delete/<str:admin>', Hod_Views.deleteStaff, name="delete_staff"),
    path('hod/staff/notify', Hod_Views.sendNotification, name="notify_staff"),
    path('hod/staff/save', Hod_Views.saveNotification, name="save_notification"),

    # HOD Alumni Path
    path('hod/alumni/membership_applications', Hod_Views.membershipApplications, name="membership_applications"),
    path('hod/alumni/membership_approval/<str:id>', Hod_Views.membershipApproved, name="membership_approved"),
    path('hod/alumni/membership_denial/<str:id>', Hod_Views.membershipDenied, name="membership_denied"),
    path('hod/alumni/feedback', Hod_Views.alumFeedback, name="alum_feedback"),
    path('hod/alumni/reply_feedback', Hod_Views.replyFeedback, name="reply_feedback"),

    # Staffs Path
    path('Staff/home', Staff_Views.homeView, name="staff_home"),
    path('Staff/Notification', Staff_Views.notification, name="notifications"),
    path('Staff/mark_as_done/<str:status>', Staff_Views.markAsDone, name="mark_as_done"),

    # Alumni Path
    path('Alumni/Home', Alumni_Views.homeView, name="alumni_home"),
    path('Alumni/ApplyForMembership', Alumni_Views.applyForMembership, name="membership_apply"),
    path('Alumni/SendApplication', Alumni_Views.saveApplication, name="save_membership"),
    path('Alumni/Feedback', Alumni_Views.alumniFeedback, name="alumni_feedback"),
    path('Alumni/SendFeedback', Alumni_Views.saveFeedback, name="save_feedback"),
]

# if MEDIA FILES are not distributed dynamically, try this fix
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
