from django.contrib import admin
from app.models import CustomUser, SessionYear, Alumni, Staff, StaffNotification, ApplyForMembership, AlumniFeedback
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class UserModel(UserAdmin):
    list_display = [
        'username', 'user_type'
    ]
admin.site.register(CustomUser, UserModel)
admin.site.register(SessionYear)
admin.site.register(Alumni)
admin.site.register(Staff)
admin.site.register(StaffNotification)
admin.site.register(ApplyForMembership)
admin.site.register(AlumniFeedback)