from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from app.profile_storage import ProfilePictureStorage


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('1', 'HOD'),
        ('2', 'Staff'),
        ('3', 'Alumni'),
        ('4', 'Student'),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=10, default='4')
    profile_pic = models.ImageField(upload_to='profile_pic', storage=ProfilePictureStorage(), blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


# ─── Original Models ────────────────────────────────────────────────────────

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    address = models.TextField(blank=True)
    gender = models.CharField(max_length=100)
    passing_year = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class SessionYear(models.Model):
    session_start = models.CharField(max_length=100)
    session_end = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.session_start} To {self.session_end}"


class Alumni(models.Model):
    BLOOD_GROUPS = [(group, group) for group in ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')]
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(default='')
    gender = models.CharField(max_length=100)
    passing_year = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    profession = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)
    current_address = models.TextField(max_length=1000, blank=True)
    permanent_address = models.TextField(max_length=1000, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    education = models.CharField(max_length=300, blank=True)
    donor_opt_in = models.BooleanField(default=False, help_text='Allow the association team to consider contacting me about a future blood donation programme. This does not confirm medical eligibility or current availability.')
    show_father_name = models.BooleanField(default=False)
    show_mother_name = models.BooleanField(default=False)
    show_current_address = models.BooleanField(default=False)
    show_permanent_address = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    show_blood_group = models.BooleanField(default=False)
    show_education = models.BooleanField(default=False)
    show_profession = models.BooleanField(default=True)
    show_company = models.BooleanField(default=True)
    show_passing_year = models.BooleanField(default=True)
    map_country = models.CharField(max_length=3, blank=True, help_text='Optional country code for the Alumni Map.')
    map_visible = models.BooleanField(default=False, help_text='Show my selected country on the public Alumni Map.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name}"

    @property
    def public_map_country(self):
        from app.map_data import countries
        return countries().get(self.map_country, {}).get('name', '') if self.map_visible else ''

    @property
    def public_profession(self):
        return self.profession if self.show_profession else ''

    @property
    def public_company(self):
        return self.company if self.show_company else ''

    @property
    def public_passing_year(self):
        return self.passing_year if self.show_passing_year else ''

    @property
    def public_details(self):
        labels = [('father_name', 'পিতার নাম'), ('mother_name', 'মাতার নাম'),
                  ('current_address', 'বর্তমান ঠিকানা'), ('permanent_address', 'স্থায়ী ঠিকানা'),
                  ('phone', 'যোগাযোগের নম্বর'), ('blood_group', 'ব্লাড গ্রুপ'),
                  ('education', 'শিক্ষাগত যোগ্যতা'), ('profession', 'পেশা'),
                  ('company', 'কর্মক্ষেত্র'), ('passing_year', 'এসএসসি ব্যাচ')]
        return [(label, getattr(self, field)) for field, label in labels
                if getattr(self, f'show_{field}') and getattr(self, field)]

    @property
    def public_detail_groups(self):
        definitions = [
            ('পরিচিতি ও পরিবার', 'Identity & family', 'fa-user', [
                ('father_name', 'পিতার নাম', 'fa-user-tie'), ('mother_name', 'মাতার নাম', 'fa-user')]),
            ('শিক্ষা ও কর্মজীবন', 'Education & career', 'fa-graduation-cap', [
                ('passing_year', 'এসএসসি ব্যাচ', 'fa-graduation-cap'), ('education', 'শিক্ষাগত যোগ্যতা', 'fa-book-open'),
                ('profession', 'পেশা', 'fa-briefcase'), ('company', 'কর্মক্ষেত্র', 'fa-building')]),
            ('যোগাযোগ ও অন্যান্য', 'Contact & details', 'fa-address-card', [
                ('phone', 'যোগাযোগের নম্বর', 'fa-phone'), ('current_address', 'বর্তমান ঠিকানা', 'fa-location-dot'),
                ('permanent_address', 'স্থায়ী ঠিকানা', 'fa-house'), ('blood_group', 'ব্লাড গ্রুপ', 'fa-droplet')]),
        ]
        groups = []
        for title, subtitle, icon, fields in definitions:
            rows = [{'label': label, 'value': getattr(self, field), 'icon': symbol}
                    for field, label, symbol in fields if getattr(self, f'show_{field}') and getattr(self, field)]
            if rows:
                groups.append({'title': title, 'subtitle': subtitle, 'icon': icon, 'rows': rows})
        return groups


class ProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.BinaryField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Staff(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(default='')
    gender = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.username


class StaffNotification(models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField(max_length=500, blank=True)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.staff_id.admin.first_name


class ApplyForMembership(models.Model):
    MEMBERSHIP_TYPES = [
        ('GENERAL', 'General Membership'),
        ('LIFE', 'Life Membership'),
        ('TRUSTEE', 'Board of Trustee Membership'),
    ]
    PAYMENT_METHODS = [
        ('BKASH', 'bKash'), ('ROCKET', 'Rocket'), ('BANK', 'Bank deposit'),
        ('CARD', 'Mastercard / VISA'), ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [(0, 'Pending'), (1, 'Approved'), (2, 'Denied')]
    alum_id = models.ForeignKey(Alumni, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=10, choices=MEMBERSHIP_TYPES, default='GENERAL')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='BKASH')
    date = models.CharField(max_length=100)
    note = models.TextField(max_length=500, blank=True)
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.alum_id.admin.first_name} {self.alum_id.admin.last_name}"


class AlumniFeedback(models.Model):
    alum_id = models.ForeignKey(Alumni, on_delete=models.CASCADE)
    feedback = models.TextField(null=True)
    feedback_reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.alum_id.admin.first_name} {self.alum_id.admin.last_name}"


# ─── Payment Records (synced from Google Sheets) ────────────────────────────

class MembershipPayment(models.Model):
    MEMBER_TYPE = [('LIFE', 'Life Member'), ('GENERAL', 'General Member')]
    STATUS = [('PAID', 'Paid'), ('PENDING', 'Pending'), ('PARTIAL', 'Partial')]

    member_name = models.CharField(max_length=200)
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPE)
    payment_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    batch_year = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='PAID')
    sheet_row_id = models.IntegerField()
    last_synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['member_type', 'member_name']
        unique_together = [('member_type', 'sheet_row_id')]

    def __str__(self):
        return f"{self.member_name} ({self.get_member_type_display()})"


# ─── Educational Content ────────────────────────────────────────────────────

class Subject(models.Model):
    GRADE_CHOICES = [
        ('CLASS_6_8', 'Class 6-8'),
        ('SSC', 'SSC (Class 9-10)'),
        ('HSC', 'HSC (Class 11-12)'),
    ]
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    icon_class = models.CharField(max_length=50, default='fa-book')

    def __str__(self):
        return f"{self.name} ({self.get_grade_display()})"


class ExamSuggestion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year = models.IntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    file = models.FileField(upload_to='suggestions/', null=True, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-year', 'subject']

    def __str__(self):
        return f"{self.title} ({self.year})"


class DailyChallenge(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(max_length=1)  # 'a', 'b', 'c', or 'd'
    explanation = models.TextField(blank=True)
    date = models.DateField(unique=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Challenge for {self.date} — {self.subject.name}"


class StudentProgress(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='progress')
    total_xp = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    challenges_completed = models.IntegerField(default=0)
    ai_queries_used = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} — {self.total_xp} XP"


# ─── Public Content ─────────────────────────────────────────────────────────

class NewsArticle(models.Model):
    CATEGORY = [
        ('EDU', 'Education'),
        ('ASSOC', 'Association'),
        ('GENERAL', 'General'),
        ('NOTICE', 'Notice'),
    ]
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=320)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    category = models.CharField(max_length=10, choices=CATEGORY, default='GENERAL')
    cover_image = models.ImageField(upload_to='news/', null=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Event(models.Model):
    ACTIVITY_TYPES = [
        ('COMMUNITY', 'Community gathering'), ('SEMINAR', 'Seminar & career talk'),
        ('GUEST_CLASS', 'Guest teaching'), ('SCHOOL_PROJECT', 'School improvement'),
        ('REUNION', 'Alumni reunion'),
    ]
    STATUS_CHOICES = [('SCHEDULED', 'Scheduled'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')]
    title = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='COMMUNITY')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='SCHEDULED')
    description = models.TextField()
    event_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    audience = models.CharField(max_length=200, blank=True, help_text='For example: Classes 9–10 or all alumni.')
    guest_faculty = models.CharField(max_length=200, blank=True, help_text='Name of the confirmed teacher or speaker, if any.')
    coordinator = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='coordinated_activities')
    students_reached = models.PositiveIntegerField(null=True, blank=True, help_text='Actual student attendance after a completed activity; leave blank until recorded.')
    outcome = models.TextField(blank=True, help_text='A short, verified account of what the activity achieved.')
    cover_image = models.ImageField(upload_to='events/', null=True, blank=True)
    registration_link = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        if self.end_date and self.event_date and self.end_date < self.event_date:
            raise ValidationError({'end_date': 'The end time must be after the start time.'})


class VolunteerApplication(models.Model):
    INTERESTS = [
        ('GUEST_CLASS', 'Teach a guest class'), ('SEMINAR', 'Lead a seminar or career talk'),
        ('SCHOOL_PROJECT', 'Support a school project'), ('COMMUNITY', 'Volunteer with the association'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'New'), ('CONTACTED', 'Contacted'), ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'), ('COMPLETED', 'Completed'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    interest = models.CharField(max_length=20, choices=INTERESTS)
    expertise = models.CharField(max_length=200)
    availability = models.CharField(max_length=200)
    message = models.TextField(max_length=2000, blank=True)
    consent_to_contact = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='NEW')
    assigned_to = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_volunteers')
    activity = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL, related_name='volunteer_applications')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.get_interest_display()}'


class GalleryPhoto(models.Model):
    title = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or f"Photo {self.pk}"


# ─── AI Chat Log ─────────────────────────────────────────────────────────────

class AIChat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.TextField()
    subject = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat by {self.user} at {self.created_at:%Y-%m-%d %H:%M}"


# ─── Committee Members (public display) ─────────────────────────────────────

class CommitteeMember(models.Model):
    ROLE_CHOICES = [
        ('PRESIDENT', 'President'),
        ('VP', 'Vice President'),
        ('SECRETARY', 'Secretary'),
        ('TREASURER', 'Treasurer'),
        ('MEMBER', 'Member'),
        ('ADVISOR', 'Advisor'),
    ]
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    photo = models.ImageField(upload_to='committee/', null=True, blank=True)
    passing_year = models.CharField(max_length=20, blank=True)
    profession = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'role']

    def __str__(self):
        return f"{self.name} — {self.get_role_display()}"
