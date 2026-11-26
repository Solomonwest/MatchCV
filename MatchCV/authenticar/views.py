from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from .forms import SignupForm, ProfileForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def landing(request):
    return render(request, "landing.html")

def signup(request):
    """Create the account and sign the new user straight in."""
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "signup.html", {"form": form})

@login_required
def profile(request):
    """View and edit the career details saved on the account."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile is saved.")
        return redirect("profile")
    return render(request, "profile.html", {"form": form})