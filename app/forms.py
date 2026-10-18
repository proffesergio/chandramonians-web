from django.contrib.auth.forms import UserCreationForm
from django import forms

from app.models import ApplyForMembership, CustomUser, VolunteerApplication
from django.utils import timezone
from app.map_data import country_choices
from app.profile_storage import MAX_AVATAR_BYTES


class ProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(required=False, strip=False, widget=forms.PasswordInput)
    map_country = forms.ChoiceField(required=False, choices=country_choices)
    map_visible = forms.BooleanField(required=False, label='Share my country on the public Alumni Map')

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'profile_pic')
        widgets = {'profile_pic': forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp,image/gif'})}

    def clean_profile_pic(self):
        picture = self.cleaned_data.get('profile_pic')
        if picture and hasattr(picture, 'content_type') and picture.size > MAX_AVATAR_BYTES:
            raise forms.ValidationError('Choose an image smaller than 3 MB.')
        return picture

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-check-input' if name == 'map_visible' else 'form-select' if name == 'map_country' else 'form-control'
        self.fields['password'].widget.attrs['autocomplete'] = 'new-password'

    def clean_password(self):
        from django.contrib.auth.password_validation import validate_password
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password, user=self.instance)
        return password

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('map_visible') and not cleaned.get('map_country'):
            self.add_error('map_country', 'Choose a country before sharing it on the map.')
        return cleaned


class ContactForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200, required=False)
    message = forms.CharField(max_length=10000)


class CommunitySignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type')

    def clean_user_type(self):
        from django.core.exceptions import ValidationError
        role = self.cleaned_data['user_type']
        if role not in ('3', '4'):
            raise ValidationError('Staff and committee accounts must be created by an administrator.')
        return role


class VolunteerApplicationForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    consent_to_contact = forms.BooleanField(
        label='I agree that the association team may contact me about this application.',
        required=True,
    )

    class Meta:
        model = VolunteerApplication
        fields = ('name', 'email', 'phone', 'interest', 'expertise', 'availability', 'message', 'consent_to_contact')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
        }
        labels = {'name': 'Your name', 'email': 'Email address (optional)', 'phone': 'Phone number (optional)',
                  'interest': 'How would you like to help?', 'expertise': 'Your subject or experience',
                  'availability': 'When are you available?', 'message': 'Anything else we should know? (optional)'}

    def clean(self):
        from django.core.exceptions import ValidationError
        cleaned = super().clean()
        if cleaned.get('website'):
            raise ValidationError('We could not accept this application. Please contact the association.')
        if not cleaned.get('email') and not cleaned.get('phone'):
            raise ValidationError('Please provide an email address or phone number so the team can contact you.')
        return cleaned


class MembershipApplicationForm(forms.ModelForm):
    date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date', 'autocomplete': 'off'}),
    )

    class Meta:
        model = ApplyForMembership
        fields = ('membership_type', 'payment_method', 'date', 'note')
        widgets = {'note': forms.Textarea(attrs={'rows': 4, 'maxlength': 500})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget.attrs.update({'class': 'form-select'})
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        self.fields['note'].widget.attrs.update({'class': 'form-control'})

    def clean_date(self):
        value = self.cleaned_data['date']
        if value > timezone.localdate():
            raise forms.ValidationError('The application date cannot be in the future.')
        return value
