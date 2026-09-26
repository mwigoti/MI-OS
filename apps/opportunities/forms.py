"""
MwohaOS Opportunities Forms — Milestone 2: Manual URL Ingestion & Editing
"""
from django import forms
from django.core.exceptions import ValidationError
from apps.opportunities.models import Opportunity
from apps.opportunities.services.security import validate_public_url
from apps.opportunities.constants import OpportunityType, Sector, OpportunityStatus


class ManualUrlIngestionForm(forms.Form):
    """
    Step 1: Enter a public opportunity webpage URL to extract metadata.
    """
    target_url = forms.URLField(
        label="Opportunity Webpage URL",
        widget=forms.URLInput(attrs={
            "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500",
            "placeholder": "https://careers.example.com/job/123 or https://grants.org/call-2026",
            "autofocus": True,
        }),
        help_text="Enter any public job, grant, fellowship, or competition link. Must be public HTTP/HTTPS.",
    )

    def clean_target_url(self):
        url = self.cleaned_data["target_url"].strip()
        try:
            validate_public_url(url)
        except ValidationError as e:
            raise ValidationError(str(e.message if hasattr(e, 'message') else e))
        return url


class OpportunityEditForm(forms.ModelForm):
    """
    Step 2: Review and edit extracted opportunity facts before persisting.
    """
    class Meta:
        model = Opportunity
        fields = [
            "title",
            "organization",
            "opportunity_type",
            "sector",
            "location",
            "country",
            "remote",
            "deadline",
            "deadline_timezone",
            "source_url",
            "application_url",
            "compensation",
            "description",
            "eligibility_text",
            "requirements",
            "preferred_skills",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "organization": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "opportunity_type": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "sector": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "location": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "country": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "remote": forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-blue-600 focus:ring-blue-500"}),
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "deadline_timezone": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "source_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "application_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "compensation": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "e.g. $95,000/yr or €25,000 grant"}),
            "description": forms.Textarea(attrs={"rows": 6, "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "eligibility_text": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "requirements": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "preferred_skills": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "Python, Earth Engine, PostGIS"}),
            "status": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
        }
