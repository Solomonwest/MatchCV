from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CV,  TailoredCV

User=get_user_model()

INPUT = (
    "w-full rounded-xl border border-neutral-300 px-3 py-2 text-sm text-black "
    "focus:border-[#CB5DF1] focus:outline-none focus:ring-2 focus:ring-[#CB5DF1]/30"
)


class CVForm(forms.ModelForm):
    """Upload of an ORIGINAL CV. Enhancement happens right after saving."""

    class Meta:
        model = CV
        fields = ["title", "file", "text_content"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": INPUT, "placeholder": "e.g. Product Designer CV, 2026"}
            ),
            "file": forms.ClearableFileInput(
                attrs={"class": "block w-full text-sm text-neutral-600"}
            ),
            "text_content": forms.Textarea(
                attrs={
                    "class": INPUT,
                    "rows": 8,
                    "placeholder": "Optional: paste your CV text instead of uploading a file",
                }
            ),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("file") and not (cleaned.get("text_content") or "").strip():
            raise forms.ValidationError("Upload a PDF or DOCX file, or paste your CV text.")
        return cleaned


class MatchForm(forms.Form):
    """Role analysis. The CV list contains ENHANCED CVs only."""

    cv = forms.ModelChoiceField(queryset= TailoredCV.objects.none(), label="Enhanced CV")
    job_title = forms.CharField(
        max_length=160,
        label="Job title",
        widget=forms.TextInput(
            attrs={"class": INPUT, "placeholder": "Senior Product Designer"}
        ),
    )
    company = forms.CharField(
        max_length=160,
        required=False,
        label="Company (optional)",
        widget=forms.TextInput(attrs={"class": INPUT, "placeholder": "Loom"}),
    )
    job_description = forms.CharField(
        label="Job description",
        widget=forms.Textarea(
            attrs={
                "class": INPUT,
                "rows": 10,
                "placeholder": "Paste the full job description, including the requirements",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cv"].queryset =  TailoredCV.objects.filter(user=user)
        self.fields["cv"].widget.attrs["class"] = INPUT

    def clean_job_description(self):
        value = self.cleaned_data["job_description"]
        if len(value.strip()) < 60:
            raise forms.ValidationError(
                "Paste the full job description, including the requirements."
            )
        return value


