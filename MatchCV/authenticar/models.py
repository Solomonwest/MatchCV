from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """The account, plus the career details that describe the job seeker.

    This model has to exist before the first migration: Django cannot swap
    AUTH_USER_MODEL on a database that already has its own auth tables.
    """

    full_name = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    linkedin_url = models.URLField(blank=True)
    target_roles = models.CharField(
        max_length=240,
        blank=True,
        help_text="The roles you are aiming for, separated by commas",
    )
    career_preferences = models.TextField(
        blank=True,
        help_text="Work arrangement, industries, seniority, anything a reader should know",
    )

    @property
    def display_name(self):
        return self.full_name.strip() or self.get_username()

    def profile_context(self):
        """The profile as plain text for the prompts. Empty fields are dropped."""
        rows = [
            ("Full name", self.full_name),
            ("Location", self.location),
            ("Phone", self.phone),
            ("LinkedIn", self.linkedin_url),
            ("Target roles", self.target_roles),
            ("Career preferences", self.career_preferences),
        ]
        return "\n".join(
            label + ": " + value.strip()
            for label, value in rows
            if value and value.strip()
        )