from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
path(
    "accounts/login/",
    auth_views.LoginView.as_view(redirect_authenticated_user=True),
    name="login",
),
path("", views.landing, name="landing"),
path("accounts/", include("django.contrib.auth.urls")),
path("signup/", views.signup, name="signup"),
path("profile/", views.profile, name="profile"),

]