"""
MwohaOS Accounts Forms
Authentication, profile settings, and preference forms.
"""
import zoneinfo
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import UserPreference

User = get_user_model()

COMMON_TIMEZONES = [
    ("Africa/Nairobi", "Africa/Nairobi (EAT, UTC+3)"),
    ("UTC", "UTC (Coordinated Universal Time)"),
    ("Africa/Lagos", "Africa/Lagos (WAT, UTC+1)"),
    ("Africa/Johannesburg", "Africa/Johannesburg (SAST, UTC+2)"),
    ("Africa/Cairo", "Africa/Cairo (EEST, UTC+2)"),
    ("Europe/London", "Europe/London (GMT/BST)"),
    ("Europe/Paris", "Europe/Paris (CET/CEST)"),
    ("Europe/Berlin", "Europe/Berlin (CET/CEST)"),
    ("America/New_York", "America/New_York (EST/EDT)"),
    ("America/Chicago", "America/Chicago (CST/CDT)"),
    ("America/Denver", "America/Denver (MST/MDT)"),
    ("America/Los_Angeles", "America/Los_Angeles (PST/PDT)"),
    ("Asia/Dubai", "Asia/Dubai (GST, UTC+4)"),
    ("Asia/Kolkata", "Asia/Kolkata (IST, UTC+5:30)"),
    ("Asia/Singapore", "Asia/Singapore (SGT, UTC+8)"),
    ("Asia/Tokyo", "Asia/Tokyo (JST, UTC+9)"),
    ("Australia/Sydney", "Australia/Sydney (AEST/AEDT)"),
]


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm",
            "placeholder": "you@example.com",
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm",
            })


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm",
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm",
            }),
        }


class UserPreferencesForm(forms.ModelForm):
    timezone = forms.ChoiceField(
        choices=COMMON_TIMEZONES,
        widget=forms.Select(attrs={
            "class": "w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm",
        }),
    )

    class Meta:
        model = UserPreference
        fields = ["timezone", "email_notifications"]
        widgets = {
            "email_notifications": forms.CheckboxInput(attrs={
                "class": "h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-slate-300 rounded",
            }),
        }
