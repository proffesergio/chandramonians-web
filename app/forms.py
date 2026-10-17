from django.contrib.auth.forms import UserCreationForm

from app.models import CustomUser


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
