from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class ProfileUserAdmin(UserAdmin):
    list_display = ("username", "email", "full_name", "location")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Career profile",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "location",
                    "linkedin_url",
                    "target_roles",
                    "career_preferences",
                )
            },
        ),
    )
