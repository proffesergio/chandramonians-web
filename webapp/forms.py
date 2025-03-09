from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import CustomUser, Student
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-control'}))
    passing_year = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Passing Year', 'class': 'form-control'}))

    class Meta:
        model = CustomUser  # ✅ Correct model
        fields = ['username', 'email', 'password1', 'password2', 'gender', 'phone', 'passing_year']