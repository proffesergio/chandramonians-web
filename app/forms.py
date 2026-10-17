from django.contrib.auth.forms import UserCreationForm
from django import forms

from app.models import CustomUser, VolunteerApplication


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
