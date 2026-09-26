"""
MwohaOS Profiles Forms — Milestone 1: Form Validation & Security
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Profile,
    Skill,
    Experience,
    Education,
    Project,
    Achievement,
    Certification,
    Publication,
    Language,
    ProfilePreference,
    Evidence,
)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "headline",
            "professional_summary",
            "location",
            "country",
            "city",
            "phone",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "personal_website_url",
            "work_authorization",
            "remote_preference",
            "availability",
        ]
        widgets = {
            "headline": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "e.g. Lead Geospatial Systems Architect & ML Engineer"}),
            "professional_summary": forms.Textarea(attrs={"rows": 4, "class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "Comprehensive summary of experience, capabilities, and target opportunities..."}),
            "location": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "Nairobi, Kenya"}),
            "country": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "Kenya"}),
            "city": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "Nairobi"}),
            "phone": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "+254 700 000000"}),
            "linkedin_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "https://linkedin.com/in/username"}),
            "github_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "https://github.com/username"}),
            "portfolio_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "https://portfolio.example.com"}),
            "personal_website_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "https://example.com"}),
            "work_authorization": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500", "placeholder": "Kenyan Citizen, Remote Contract Globally"}),
            "remote_preference": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
            "availability": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm focus:border-blue-500 focus:ring-blue-500"}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "category", "proficiency", "years_experience", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. Python, Google Earth Engine, PostGIS"}),
            "category": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "proficiency": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "years_experience": forms.NumberInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. 4.5", "step": "0.5"}),
            "description": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Key practical context..."}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "organization",
            "position",
            "employment_type",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "description",
            "achievements",
            "url",
        ]
        widgets = {
            "organization": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Organization / Company Name"}),
            "position": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Job Title"}),
            "employment_type": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "location": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Nairobi, Kenya or Remote"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "is_current": forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-blue-600"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm"}),
            "achievements": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Quantified outcomes and measurable deliverables..."}),
            "url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "https://company.org"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get("is_current")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not is_current and start_date and end_date:
            if end_date < start_date:
                raise ValidationError({"end_date": "End date cannot be prior to start date."})
        return cleaned_data


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "degree",
            "field_of_study",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "grade",
            "description",
            "url",
        ]
        widgets = {
            "institution": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "University / Institution"}),
            "degree": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. Bachelor of Science"}),
            "field_of_study": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. Geomatics Engineering"}),
            "location": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "City, Country"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "is_current": forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-blue-600"}),
            "grade": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. First Class Honours / 3.8 GPA"}),
            "description": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 text-sm"}),
            "url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get("is_current")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not is_current and start_date and end_date:
            if end_date < start_date:
                raise ValidationError({"end_date": "End date cannot be prior to start date."})
        return cleaned_data


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "category",
            "role",
            "technologies",
            "description",
            "impact",
            "start_date",
            "end_date",
            "is_current",
            "url",
            "repository_url",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Project Title"}),
            "category": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "role": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. Lead Engineer"}),
            "technologies": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Python, Sentinel-2, PostGIS, Docker"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm"}),
            "impact": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Measurable outcomes, publications, active users..."}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "is_current": forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-blue-600"}),
            "url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "https://demo.app"}),
            "repository_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "https://github.com/..."}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get("is_current")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not is_current and start_date and end_date:
            if end_date < start_date:
                raise ValidationError({"end_date": "End date cannot be prior to start date."})
        return cleaned_data


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "organization", "date", "description", "url"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Award or Recognition Title"}),
            "organization": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Issuing Organization"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm"}),
            "url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["name", "issuer", "credential_id", "credential_url", "issue_date", "expiry_date", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Certification Title"}),
            "issuer": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Issuing Body"}),
            "credential_id": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "credential_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "issue_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "expiry_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "description": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 text-sm"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get("issue_date")
        expiry_date = cleaned_data.get("expiry_date")
        if issue_date and expiry_date:
            if expiry_date < issue_date:
                raise ValidationError({"expiry_date": "Expiry date cannot be prior to issue date."})
        return cleaned_data


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ["title", "publication_type", "publisher", "authors", "publication_date", "doi", "url", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "publication_type": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "publisher": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "authors": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "publication_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border-slate-300 text-sm"}),
            "doi": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "10.1000/182"}),
            "url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm"}),
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ["language", "proficiency"]
        widgets = {
            "language": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. English, French, Swahili"}),
            "proficiency": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
        }


class ProfilePreferenceForm(forms.ModelForm):
    OPPORTUNITY_CHOICES = [
        ("Jobs", "Full-time & Part-time Jobs"),
        ("Internships", "Internships"),
        ("Fellowships", "Fellowships"),
        ("Grants", "Grants & Funding"),
        ("Accelerators", "Accelerators"),
        ("Incubators", "Incubators"),
        ("Scholarships", "Scholarships"),
        ("Research", "Research Positions"),
        ("Competitions", "Competitions"),
        ("Hackathons", "Hackathons"),
        ("Consulting", "Consulting Contracts"),
        ("Freelance", "Freelance Projects"),
        ("Training", "Training Programs"),
    ]

    SECTOR_CHOICES = [
        ("Geospatial", "Geospatial & GIS"),
        ("Earth Observation", "Earth Observation & Remote Sensing"),
        ("Space", "Space Systems & Satellite Tech"),
        ("Climate", "Climate & Meteorology"),
        ("Agriculture", "Agriculture & Food Security"),
        ("AI", "Artificial Intelligence & ML"),
        ("Software", "Software Engineering"),
        ("Data", "Data Science & Big Data"),
        ("Research", "Scientific Research"),
        ("Environment", "Environment & Natural Resources"),
        ("Disaster Risk", "Disaster Risk & Emergency Response"),
        ("Entrepreneurship", "Entrepreneurship & Startups"),
    ]

    WORK_MODE_CHOICES = [
        ("Remote", "Remote Only"),
        ("Hybrid", "Hybrid"),
        ("Onsite", "On-site"),
    ]

    target_opportunity_types = forms.MultipleChoiceField(
        choices=OPPORTUNITY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "rounded border-slate-300 text-blue-600"}),
        required=False,
    )
    target_sectors = forms.MultipleChoiceField(
        choices=SECTOR_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "rounded border-slate-300 text-blue-600"}),
        required=False,
    )
    work_modes = forms.MultipleChoiceField(
        choices=WORK_MODE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "rounded border-slate-300 text-blue-600"}),
        required=False,
    )

    class Meta:
        model = ProfilePreference
        fields = [
            "target_opportunity_types",
            "target_sectors",
            "work_modes",
            "target_countries",
            "target_regions",
            "min_compensation",
            "additional_notes",
        ]
        widgets = {
            "target_countries": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. Kenya, United States, United Kingdom, Global"}),
            "target_regions": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. East Africa, Sub-Saharan Africa, Global"}),
            "min_compensation": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. $80,000/yr or $5,000/grant"}),
            "additional_notes": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border-slate-300 text-sm"}),
        }


class EvidenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)
        if profile:
            # Filter foreign key dropdowns to this profile's owned records only
            from apps.documents.models import Document
            self.fields["document"].queryset = Document.objects.filter(profile=profile)
            self.fields["related_project"].queryset = Project.objects.filter(profile=profile)
            self.fields["related_experience"].queryset = Experience.objects.filter(profile=profile)
            self.fields["related_education"].queryset = Education.objects.filter(profile=profile)
            self.fields["related_achievement"].queryset = Achievement.objects.filter(profile=profile)
            self.fields["related_certification"].queryset = Certification.objects.filter(profile=profile)

    class Meta:
        model = Evidence
        fields = [
            "title",
            "evidence_type",
            "claim_summary",
            "description",
            "source_url",
            "document",
            "related_project",
            "related_experience",
            "related_education",
            "related_achievement",
            "related_certification",
            "verified",
            "verification_notes",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "e.g. GitHub: FloodRisk-Sentinel Pipeline Repository"}),
            "evidence_type": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "claim_summary": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "The specific claim or capability supported by this record..."}),
            "description": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 text-sm"}),
            "source_url": forms.URLInput(attrs={"class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "https://github.com/..."}),
            "document": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "related_project": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "related_experience": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "related_education": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "related_achievement": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "related_certification": forms.Select(attrs={"class": "w-full rounded-md border-slate-300 text-sm"}),
            "verified": forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-emerald-600"}),
            "verification_notes": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-md border-slate-300 text-sm", "placeholder": "Verified via institutional letter / domain email / repo commit logs..."}),
        }
