from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):

    # USERNAME_FIELD = 'email'  # Use email for authentication
    # REQUIRED_FIELDS = ['username']  # Keep username as required

    USER_TYPE_CHOICES = (
        ('1', 'HOD'),
        ('2', 'STAFF'),
        ('3', 'ALUMNI'),
        ('4', 'STUDENT'),
    )

    email = models.EmailField(unique=True)  # Ensure email is unique
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=10, default='4')
    profile_pic = models.ImageField(upload_to='media/profile_pic', blank=True, null=True)

    USERNAME_FIELD = 'email'  # Use email instead of username
    REQUIRED_FIELDS = ['username']  # Keep username required

    def __str__(self):
        return self.email

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile', default=None)
    address = models.TextField(default=None, blank=True)
    gender = models.CharField(max_length=100)
    passing_year = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.user.username

class SessionYear(models.Model):
    session_start = models.CharField(max_length=100)
    session_end = models.CharField(max_length=100)

    def __str__(self):
        return self.session_start + " To " + self.session_end

class Alumni(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(default=None)
    gender = models.CharField(max_length=100)
    passing_year = models.CharField(max_length=20, null=True)
    phone = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # org_name = models.CharField(max_length=100, default=None)
    # passing_year = models.ForeignKey(SessionYear, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.admin.first_name + " " + self.admin.last_name

class Staff(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(default=None)
    gender = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.username

class StaffNotification(models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.staff_id.admin.first_name

class ApplyForMembership(models.Model):
    alum_id = models.ForeignKey(Alumni, on_delete=models.CASCADE)
    date = models.CharField(max_length=100)
    note = models.TextField(blank=True, max_length=500)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alum_id.admin.first_name + self.alum_id.admin.last_name

class AlumniFeedback(models.Model):
    alum_id = models.ForeignKey(Alumni, on_delete=models.CASCADE)
    feedback = models.TextField(null=True)
    feedback_reply = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alum_id.admin.first_name + self.alum_id.admin.last_name