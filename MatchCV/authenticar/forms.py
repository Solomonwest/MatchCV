from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from django.db import models

INPUT = (
    "w-full rounded-xl border border-neutral-300 px-3 py-2 text-sm text-black "
    "focus:border-[#CB5DF1] focus:outline-none focus:ring-2 focus:ring-[#CB5DF1]/30"
)

PROFILE_WIDGETS = {
    "full_name": forms.TextInput(attrs={"class": INPUT, "placeholder": "Ada Obi"}),
    "phone": forms.TextInput(
        attrs={"class": INPUT, "placeholder": "+234 800 000 0000"}
    ),
    "location": forms.TextInput(attrs={"class": INPUT, "placeholder": "Lagos, Nigeria"}),
    "linkedin_url": forms.URLInput(
        attrs={"class": INPUT, "placeholder": "https://www.linkedin.com/in/your-name"}
    ),
    "target_roles": forms.TextInput(
        attrs={"class": INPUT, "placeholder": "Product Designer, UX Lead"}
    ),
    "career_preferences": forms.Textarea(
        attrs={
            "class": INPUT,
            "rows": 4,
            "placeholder": "Remote-first, fintech, senior individual contributor",
        }
    ),
}

User = get_user_model()


class SignupForm(UserCreationForm):
    """Account creation, collecting the career profile up front."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "full_name",
            "phone",
            "location",
            "linkedin_url",
            "target_roles",
            "career_preferences",
            "password1",
            "password2",
        )
        widgets = {
            "username": forms.TextInput(attrs={"class": INPUT, "autofocus": True}),
            "email": forms.EmailInput(attrs={"class": INPUT}),
            **PROFILE_WIDGETS,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs.update({"class": INPUT})


class ProfileForm(forms.ModelForm):
    """Editing the career profile saved on the account."""

    class Meta:
        model = User
        fields = (
            "full_name",
            "phone",
            "location",
            "linkedin_url",
            "target_roles",
            "career_preferences",
        )
        widgets = PROFILE_WIDGETS