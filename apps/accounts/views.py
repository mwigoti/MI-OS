"""
MwohaOS Accounts Views
Authentication, registration, user settings, and preference management.
"""
import sys
import django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
    PasswordChangeView as DjangoPasswordChangeView,
    PasswordChangeDoneView as DjangoPasswordChangeDoneView,
    PasswordResetView as DjangoPasswordResetView,
    PasswordResetDoneView as DjangoPasswordResetDoneView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
    PasswordResetCompleteView as DjangoPasswordResetCompleteView,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import RegistrationForm, AccountUpdateForm, UserPreferencesForm
from .models import UserPreference


class LoginView(DjangoLoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("core:dashboard")


def logout_view(request: HttpRequest) -> HttpResponse:
    """Logs out user and redirects to login page."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


def register_view(request: HttpRequest) -> HttpResponse:
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MwohaOS, {user.username}! Your account is ready.")
            return redirect("core:dashboard")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def settings_view(request: HttpRequest) -> HttpResponse:
    """
    Settings Page
    Section 19:
    Account:
    - Username
    - Email
    - Password change
    Preferences:
    - Timezone
    - Email notifications enabled/disabled
    System:
    - Application version
    - Environment
    """
    pref, _ = UserPreference.objects.get_or_create(
        user=request.user,
        defaults={"timezone": getattr(settings, "TIME_ZONE", "Africa/Nairobi")}
    )

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_account":
            account_form = AccountUpdateForm(request.POST, instance=request.user)
            pref_form = UserPreferencesForm(instance=pref)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "Account details updated successfully.")
                return redirect("accounts:settings")
        elif action == "update_preferences":
            pref_form = UserPreferencesForm(request.POST, instance=pref)
            account_form = AccountUpdateForm(instance=request.user)
            if pref_form.is_valid():
                pref_form.save()
                messages.success(request, "Preferences updated successfully.")
                return redirect("accounts:settings")
        else:
            account_form = AccountUpdateForm(instance=request.user)
            pref_form = UserPreferencesForm(instance=pref)
    else:
        account_form = AccountUpdateForm(instance=request.user)
        pref_form = UserPreferencesForm(instance=pref)

    context = {
        "account_form": account_form,
        "pref_form": pref_form,
        "system_info": {
            "app_version": getattr(settings, "APP_VERSION", "0.1.0-milestone-0"),
            "environment": "Development" if settings.DEBUG else "Production",
            "django_version": django.get_version(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "database_engine": settings.DATABASES["default"]["ENGINE"].split(".")[-1],
            "default_timezone": getattr(settings, "TIME_ZONE", "Africa/Nairobi"),
        },
    }
    return render(request, "settings/index.html", context)


class PasswordChangeView(DjangoPasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("accounts:password_change_done")


class PasswordChangeDoneView(DjangoPasswordChangeDoneView):
    template_name = "registration/password_change_done.html"


class PasswordResetView(DjangoPasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
