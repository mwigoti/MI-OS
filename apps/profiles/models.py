"""
MwohaOS Profiles Models — Milestone 1: Professional Profile & Evidence System.
Factual, structured, evidence-backed representation of professional identity.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import TimeStampedModel


class Profile(TimeStampedModel):
    """
    Central 1-to-1 Profile model for the authenticated user.
    Acts as the root anchor for all career credentials, preferences, evidence, and documents.
    """

    class RemotePreference(models.TextChoices):
        REMOTE_ONLY = "REMOTE_ONLY", "Remote Only"
        HYBRID = "HYBRID", "Hybrid"
        ONSITE = "ONSITE", "On-site"
        FLEXIBLE = "FLEXIBLE", "Flexible"

    class Availability(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available Immediately"
        OPEN_TO_OPPORTUNITIES = "OPEN_TO_OPPORTUNITIES", "Open to Opportunities"
        EMPLOYED = "EMPLOYED", "Employed / Exploring Selectively"
        NOT_AVAILABLE = "NOT_AVAILABLE", "Not Available"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    headline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Professional title or headline (e.g. Geospatial Data Scientist & ML Engineer).",
    )
    professional_summary = models.TextField(
        blank=True,
        help_text="Factual summary of professional background, focus areas, and domain expertise.",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="City, State / Region (e.g. Nairobi, Kenya).",
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary country of residence (e.g. Kenya).",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City of residence.",
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Contact telephone / mobile number.",
    )
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL.",
    )
    github_url = models.URLField(
        blank=True,
        help_text="GitHub profile URL.",
    )
    portfolio_url = models.URLField(
        blank=True,
        help_text="Personal portfolio or project catalog URL.",
    )
    personal_website_url = models.URLField(
        blank=True,
        help_text="Personal website or blog URL.",
    )
    work_authorization = models.CharField(
        max_length=255,
        blank=True,
        help_text="Work authorization status (e.g. Kenyan Citizen, US F-1 OPT Eligible, Global Remote Contractor).",
    )
    remote_preference = models.CharField(
        max_length=50,
        choices=RemotePreference.choices,
        default=RemotePreference.FLEXIBLE,
        help_text="Work arrangement preference.",
    )
    availability = models.CharField(
        max_length=50,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
        help_text="Current availability status for opportunities.",
    )

    class Meta:
        verbose_name = "Professional Profile"
        verbose_name_plural = "Professional Profiles"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


class Skill(TimeStampedModel):
    """
    Structured skill records with verified proficiency and category.
    """

    class Category(models.TextChoices):
        TECHNICAL = "TECHNICAL", "Technical"
        GEOSPATIAL = "GEOSPATIAL", "Geospatial"
        REMOTE_SENSING = "REMOTE_SENSING", "Remote Sensing"
        SOFTWARE = "SOFTWARE", "Software Engineering"
        DATA = "DATA", "Data Science & Analytics"
        AI_ML = "AI_ML", "AI & Machine Learning"
        CLIMATE = "CLIMATE", "Climate & Earth Observation"
        AGRICULTURE = "AGRICULTURE", "Agriculture & Food Systems"
        RESEARCH = "RESEARCH", "Research & Methodology"
        BUSINESS = "BUSINESS", "Business & Strategy"
        LEADERSHIP = "LEADERSHIP", "Leadership & Management"
        COMMUNICATION = "COMMUNICATION", "Communication & Writing"
        OTHER = "OTHER", "Other"

    class Proficiency(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"
        EXPERT = "EXPERT", "Expert"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    name = models.CharField(
        max_length=150,
        db_index=True,
        help_text="Skill name (e.g. Python, Google Earth Engine, QGIS, PyTorch).",
    )
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.TECHNICAL,
    )
    proficiency = models.CharField(
        max_length=30,
        choices=Proficiency.choices,
        default=Proficiency.INTERMEDIATE,
    )
    years_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Estimated years of practical experience with this skill.",
    )
    description = models.TextField(
        blank=True,
        help_text="Specific contextual details, tools, or projects where this skill was applied.",
    )

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ["category", "name"]
        unique_together = [["profile", "name"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_proficiency_display()})"


class Experience(TimeStampedModel):
    """
    Employment and professional experience records.
    """

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full-time"
        PART_TIME = "PART_TIME", "Part-time"
        CONTRACT = "CONTRACT", "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"
        FREELANCE = "FREELANCE", "Freelance"
        CONSULTING = "CONSULTING", "Consulting"
        VOLUNTEER = "VOLUNTEER", "Volunteer"
        FOUNDER = "FOUNDER", "Founder"
        OTHER = "OTHER", "Other"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="experiences",
    )
    organization = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Company, institution, or organization name.",
    )
    position = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Job title or role.",
    )
    employment_type = models.CharField(
        max_length=50,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Location of work (or Remote).",
    )
    start_date = models.DateField(
        help_text="Role start date.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Role end date (leave empty if current).",
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Check if you currently hold this position.",
    )
    description = models.TextField(
        blank=True,
        help_text="Core responsibilities and duties.",
    )
    achievements = models.TextField(
        blank=True,
        help_text="Key achievements, metrics, and measurable outcomes.",
    )
    url = models.URLField(
        blank=True,
        help_text="Organization website or project verification link.",
    )

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"
        ordering = ["-is_current", "-start_date"]

    def clean(self):
        super().clean()
        if not self.is_current and self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({"end_date": "End date cannot be prior to start date."})

    def __str__(self) -> str:
        return f"{self.position} at {self.organization}"


class Education(TimeStampedModel):
    """
    Formal education and academic credentials.
    """
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="education",
    )
    institution = models.CharField(
        max_length=255,
        db_index=True,
        help_text="University, college, or academic institution name.",
    )
    degree = models.CharField(
        max_length=255,
        help_text="Degree or credential (e.g. Bachelor of Science, Master of Science).",
    )
    field_of_study = models.CharField(
        max_length=255,
        help_text="Field of study or major (e.g. Geomatics Engineering, Computer Science).",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Institution city, country.",
    )
    start_date = models.DateField(
        help_text="Start date of studies.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Graduation / completion date (leave blank if ongoing).",
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Check if you are currently enrolled.",
    )
    description = models.TextField(
        blank=True,
        help_text="Relevant coursework, academic honors, or thesis topic.",
    )
    grade = models.CharField(
        max_length=100,
        blank=True,
        help_text="GPA, honors classification, or grading result (optional).",
    )
    url = models.URLField(
        blank=True,
        help_text="Institution or program verification link.",
    )

    class Meta:
        verbose_name = "Education Record"
        verbose_name_plural = "Education Records"
        ordering = ["-is_current", "-start_date"]

    def clean(self):
        super().clean()
        if not self.is_current and self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({"end_date": "End date cannot be prior to start date."})

    def __str__(self) -> str:
        return f"{self.degree} in {self.field_of_study} from {self.institution}"


class Project(TimeStampedModel):
    """
    Tangible projects demonstrating applied capability and impact.
    """

    class Category(models.TextChoices):
        GEOSPATIAL = "GEOSPATIAL", "Geospatial & Remote Sensing"
        EARTH_OBSERVATION = "EARTH_OBSERVATION", "Earth Observation & Satellite"
        CLIMATE = "CLIMATE", "Climate & Environment"
        AGRICULTURE = "AGRICULTURE", "Agriculture & Precision Farming"
        SOFTWARE = "SOFTWARE", "Software & Systems Architecture"
        AI = "AI", "Artificial Intelligence & ML"
        RESEARCH = "RESEARCH", "Scientific & Applied Research"
        COMMUNITY = "COMMUNITY", "Open Source & Community"
        ENTREPRENEURSHIP = "ENTREPRENEURSHIP", "Entrepreneurship & Commercial"
        OTHER = "OTHER", "Other"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Project title.",
    )
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.GEOSPATIAL,
    )
    role = models.CharField(
        max_length=150,
        blank=True,
        help_text="Your role (e.g. Lead Developer, Principal Investigator).",
    )
    technologies = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tools & stacks (e.g. Python, Sentinel-2, GDAL, Django, Docker).",
    )
    description = models.TextField(
        help_text="Clear factual summary of project scope, problem tackled, and technical approach.",
    )
    impact = models.TextField(
        blank=True,
        help_text="Measurable results, user adoption, publications, or practical outcomes.",
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project start date.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Completion date (leave empty if ongoing).",
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Check if this project is actively ongoing.",
    )
    url = models.URLField(
        blank=True,
        help_text="Live demonstration or production system URL.",
    )
    repository_url = models.URLField(
        blank=True,
        help_text="Public GitHub or GitLab repository URL.",
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-is_current", "-start_date"]

    def clean(self):
        super().clean()
        if not self.is_current and self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({"end_date": "End date cannot be prior to start date."})

    def __str__(self) -> str:
        return self.name


class Achievement(TimeStampedModel):
    """
    Awards, fellowships, competition wins, and recognitions.
    """
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="achievements",
    )
    title = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Award or recognition title (e.g. NASA Space Apps Winner, Copernicus Hackathon 1st Place).",
    )
    organization = models.CharField(
        max_length=255,
        help_text="Awarding institution or organizing body.",
    )
    date = models.DateField(
        null=True,
        blank=True,
        help_text="Date awarded or achieved.",
    )
    description = models.TextField(
        blank=True,
        help_text="Context of the achievement, selection criteria, or prize.",
    )
    url = models.URLField(
        blank=True,
        help_text="Official announcement, certificate link, or news release.",
    )

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.organization})"


class Certification(TimeStampedModel):
    """
    Industry and professional certifications, licenses, and verified accreditations.
    """
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="certifications",
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Certification title (e.g. AWS Certified Solutions Architect, GISP Certification).",
    )
    issuer = models.CharField(
        max_length=255,
        help_text="Issuing authority or body (e.g. Amazon Web Services, GISCI).",
    )
    credential_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="License or credential ID.",
    )
    credential_url = models.URLField(
        blank=True,
        help_text="Verification link on the issuer's validation portal.",
    )
    issue_date = models.DateField(
        help_text="Date certification was issued.",
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date (leave blank if does not expire).",
    )
    description = models.TextField(
        blank=True,
        help_text="Summary of competencies or domains covered.",
    )

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["-issue_date"]

    def clean(self):
        super().clean()
        if self.expiry_date and self.issue_date:
            if self.expiry_date < self.issue_date:
                raise ValidationError({"expiry_date": "Expiry date cannot be prior to issue date."})

    def __str__(self) -> str:
        return f"{self.name} by {self.issuer}"


class Publication(TimeStampedModel):
    """
    Academic publications, preprints, technical reports, and peer-reviewed articles.
    """

    class PublicationType(models.TextChoices):
        JOURNAL = "JOURNAL", "Journal Article"
        CONFERENCE = "CONFERENCE", "Conference Paper"
        PREPRINT = "PREPRINT", "Preprint (arXiv/EarthArXiv)"
        TECHNICAL_REPORT = "TECHNICAL_REPORT", "Technical Report"
        ARTICLE = "ARTICLE", "Article / Technical Monograph"
        THESIS = "THESIS", "Thesis / Dissertation"
        BOOK = "BOOK", "Book / Book Chapter"
        OTHER = "OTHER", "Other"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="publications",
    )
    title = models.CharField(
        max_length=300,
        help_text="Publication title.",
    )
    publication_type = models.CharField(
        max_length=50,
        choices=PublicationType.choices,
        default=PublicationType.JOURNAL,
    )
    publisher = models.CharField(
        max_length=255,
        blank=True,
        help_text="Publisher, journal name, or conference proceeding.",
    )
    authors = models.CharField(
        max_length=500,
        blank=True,
        help_text="Author list as published (e.g. Mwoha, H., Smith, J.).",
    )
    publication_date = models.DateField(
        null=True,
        blank=True,
        help_text="Publication or release date.",
    )
    doi = models.CharField(
        max_length=150,
        blank=True,
        help_text="Digital Object Identifier (DOI).",
    )
    url = models.URLField(
        blank=True,
        help_text="Link to published paper, PDF, or DOI landing page.",
    )
    description = models.TextField(
        blank=True,
        help_text="Abstract or brief summary of findings.",
    )

    class Meta:
        verbose_name = "Publication"
        verbose_name_plural = "Publications"
        ordering = ["-publication_date", "-created_at"]

    def __str__(self) -> str:
        return self.title


class Language(TimeStampedModel):
    """
    Spoken and written language competencies.
    """

    class Proficiency(models.TextChoices):
        BASIC = "BASIC", "Basic / Elementary"
        CONVERSATIONAL = "CONVERSATIONAL", "Conversational"
        PROFESSIONAL = "PROFESSIONAL", "Professional Working"
        FLUENT = "FLUENT", "Full Professional / Fluent"
        NATIVE = "NATIVE", "Native / Bilingual"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="languages",
    )
    language = models.CharField(
        max_length=100,
        help_text="Language name (e.g. English, Swahili, French).",
    )
    proficiency = models.CharField(
        max_length=50,
        choices=Proficiency.choices,
        default=Proficiency.PROFESSIONAL,
    )

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ["language"]
        unique_together = [["profile", "language"]]

    def __str__(self) -> str:
        return f"{self.language} ({self.get_proficiency_display()})"


class ProfilePreference(TimeStampedModel):
    """
    User opportunity matching constraints and target parameters.
    Fully user-controlled — no automated guessing.
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="preferences",
    )
    # Target opportunity types stored as comma-separated choices or JSON list
    target_opportunity_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Target opportunity types (e.g. Jobs, Fellowships, Grants, Accelerators, Research).",
    )
    target_sectors = models.JSONField(
        default=list,
        blank=True,
        help_text="Target industry sectors (e.g. Geospatial, Earth Observation, Climate, Agriculture, AI).",
    )
    work_modes = models.JSONField(
        default=list,
        blank=True,
        help_text="Target work modes (Remote, Hybrid, On-site).",
    )
    target_countries = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated countries of interest (e.g. Kenya, United States, United Kingdom, Global).",
    )
    target_regions = models.CharField(
        max_length=500,
        blank=True,
        help_text="Target regions (e.g. East Africa, Sub-Saharan Africa, North America, Europe, Global).",
    )
    min_compensation = models.CharField(
        max_length=150,
        blank=True,
        help_text="Minimum desired compensation or grant threshold (optional).",
    )
    additional_notes = models.TextField(
        blank=True,
        help_text="Any additional explicit constraints or preferences for opportunity evaluation.",
    )

    class Meta:
        verbose_name = "Profile Preference"
        verbose_name_plural = "Profile Preferences"

    def __str__(self) -> str:
        return f"Preferences for {self.profile.user.username}"


class ProfileVersion(TimeStampedModel):
    """
    Historical version log of profile modifications.
    Supports future application snapshots so submissions can reference exact state at submission.
    """
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.PositiveIntegerField(
        help_text="Monotonically increasing version number.",
    )
    change_summary = models.CharField(
        max_length=255,
        help_text="Brief description of what was changed or updated.",
    )
    snapshot_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured snapshot payload of profile state at this version.",
    )

    class Meta:
        verbose_name = "Profile Version"
        verbose_name_plural = "Profile Versions"
        ordering = ["-version"]
        unique_together = [["profile", "version"]]

    def __str__(self) -> str:
        return f"v{self.version} of {self.profile.user.username} ({self.change_summary})"


class Evidence(TimeStampedModel):
    """
    Structured proof linking a claim to verified physical, digital, or organizational sources.
    Every claim in future applications (e.g. 'Built flood forecasting model', 'Published in IEEE')
    can point directly to this evidence bank.
    """

    class EvidenceType(models.TextChoices):
        CV = "CV", "Curriculum Vitae / Resume"
        CERTIFICATE = "CERTIFICATE", "Official Certificate"
        PROJECT = "PROJECT", "Project Demonstration"
        GITHUB_REPOSITORY = "GITHUB_REPOSITORY", "Code Repository (GitHub/GitLab)"
        PORTFOLIO = "PORTFOLIO", "Portfolio Item"
        PUBLICATION = "PUBLICATION", "Academic / Technical Publication"
        AWARD = "AWARD", "Award / Competition Win"
        EMPLOYMENT = "EMPLOYMENT", "Employment Verification"
        EDUCATION = "EDUCATION", "Academic Degree / Transcript"
        REFERENCE = "REFERENCE", "Reference / Recommendation"
        OTHER = "OTHER", "Other Source"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="evidence_items",
    )
    evidence_type = models.CharField(
        max_length=50,
        choices=EvidenceType.choices,
        default=EvidenceType.PROJECT,
        db_index=True,
    )
    title = models.CharField(
        max_length=255,
        help_text="Clear title of what this evidence proves (e.g. GitHub: FloodRisk-Sentinel Pipeline).",
    )
    claim_summary = models.TextField(
        blank=True,
        help_text="The specific professional claim or competency this evidence substantiates.",
    )
    description = models.TextField(
        blank=True,
        help_text="Factual explanation of the evidence, methodology, or context.",
    )
    source_url = models.URLField(
        blank=True,
        help_text="Direct verifiable link (GitHub repo, published paper, live app, certification verify URL).",
    )
    document = models.ForeignKey(
        "documents.Document",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supporting_evidence",
        help_text="Optional attached document from your Document Vault supporting this claim.",
    )

    # Explicit relationships to profile entities (No generic foreign keys; clean Django relations)
    related_project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evidence_records",
        help_text="Associated Project record.",
    )
    related_experience = models.ForeignKey(
        Experience,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evidence_records",
        help_text="Associated Experience record.",
    )
    related_education = models.ForeignKey(
        Education,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evidence_records",
        help_text="Associated Education record.",
    )
    related_achievement = models.ForeignKey(
        Achievement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evidence_records",
        help_text="Associated Achievement record.",
    )
    related_certification = models.ForeignKey(
        Certification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evidence_records",
        help_text="Associated Certification record.",
    )

    # Verification state (defaults safely to False; manually verified by user or explicit proof)
    verified = models.BooleanField(
        default=False,
        help_text="Mark True if verified against primary documentation, URL, or official record.",
    )
    verification_notes = models.TextField(
        blank=True,
        help_text="Audit notes on how this evidence was verified.",
    )

    class Meta:
        verbose_name = "Evidence Item"
        verbose_name_plural = "Evidence Bank"
        ordering = ["-verified", "-created_at"]

    def __str__(self) -> str:
        status = "Verified" if self.verified else "Unverified"
        return f"[{status}] {self.title} ({self.get_evidence_type_display()})"

