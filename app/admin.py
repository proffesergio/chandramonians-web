from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.models import (
    CustomUser, Student, Alumni, Staff, SessionYear,
    StaffNotification, ApplyForMembership, AlumniFeedback,
    MembershipPayment, Subject, ExamSuggestion, DailyChallenge,
    StudentProgress, NewsArticle, Event, GalleryPhoto, AIChat,
    CommitteeMember,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Chandramonians', {'fields': ('user_type', 'profile_pic')}),
    )


@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('admin', 'passing_year', 'gender', 'phone', 'profession', 'company')
    list_filter = ('passing_year', 'gender')
    search_fields = ('admin__first_name', 'admin__last_name', 'admin__email', 'profession')


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('admin', 'gender', 'phone', 'created_at')
    search_fields = ('admin__first_name', 'admin__last_name', 'admin__email')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'passing_year', 'gender', 'phone')
    list_filter = ('passing_year', 'gender')
    search_fields = ('user__email', 'user__username')


@admin.register(ApplyForMembership)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ('alum_id', 'date', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('alum_id__admin__first_name', 'alum_id__admin__last_name')
    actions = ['approve', 'deny']

    def approve(self, request, queryset):
        queryset.update(status=1)
    approve.short_description = 'Approve selected applications'

    def deny(self, request, queryset):
        queryset.update(status=2)
    deny.short_description = 'Deny selected applications'


@admin.register(AlumniFeedback)
class AlumniFeedbackAdmin(admin.ModelAdmin):
    list_display = ('alum_id', 'created_at', 'has_reply')
    search_fields = ('alum_id__admin__first_name',)

    def has_reply(self, obj):
        return bool(obj.feedback_reply)
    has_reply.boolean = True
    has_reply.short_description = 'Replied'


@admin.register(StaffNotification)
class StaffNotificationAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'message', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(MembershipPayment)
class MembershipPaymentAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'member_type', 'batch_year', 'payment_date', 'amount', 'status', 'last_synced_at')
    list_filter = ('member_type', 'status', 'batch_year')
    search_fields = ('member_name', 'receipt_number', 'phone')
    readonly_fields = ('sheet_row_id', 'last_synced_at')
    ordering = ('member_type', 'member_name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'icon_class')
    list_filter = ('grade',)


@admin.register(ExamSuggestion)
class ExamSuggestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'year', 'uploaded_by', 'is_published', 'created_at')
    list_filter = ('subject__grade', 'year', 'is_published')
    search_fields = ('title',)
    actions = ['publish', 'unpublish']

    def publish(self, request, queryset):
        queryset.update(is_published=True)
    publish.short_description = 'Publish selected suggestions'

    def unpublish(self, request, queryset):
        queryset.update(is_published=False)
    unpublish.short_description = 'Unpublish selected suggestions'


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('date', 'subject', 'created_by')
    list_filter = ('subject',)
    ordering = ('-date',)


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_xp', 'current_streak', 'longest_streak', 'challenges_completed')
    ordering = ('-total_xp',)
    readonly_fields = ('user',)


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'published_at', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['publish', 'unpublish']

    def publish(self, request, queryset):
        queryset.update(is_published=True)
    publish.short_description = 'Publish selected articles'

    def unpublish(self, request, queryset):
        queryset.update(is_published=False)
    unpublish.short_description = 'Unpublish selected articles'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'location')
    ordering = ('-event_date',)


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'uploaded_at')
    list_filter = ('category',)
    search_fields = ('title', 'category')


@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at')
    list_filter = ('subject',)
    search_fields = ('user__email', 'question')
    readonly_fields = ('user', 'session_id', 'question', 'answer', 'subject', 'created_at')


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'passing_year', 'profession', 'order')
    list_filter = ('role',)
    ordering = ('order',)


admin.site.register(SessionYear)
