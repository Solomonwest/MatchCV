from django.contrib import admin

from .models import CV, TailoredCV, Match




@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "uploaded_at")


@admin.register(TailoredCV)
class TailoredCVAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_default", "created_at")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("job_title", "company", "overall_score", "verdict", "user", "created_at")
