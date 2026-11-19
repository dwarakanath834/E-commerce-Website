from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class AccountDetailsForm(forms.ModelForm):
    phone = forms.CharField(max_length=24, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)
        if self.profile:
            self.fields["phone"].initial = self.profile.phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit and self.profile:
            self.profile.phone = self.cleaned_data["phone"]
            self.profile.save(update_fields=["phone", "updated_at"])
        return user