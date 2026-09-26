"""
MwohaOS Profiles Migration 0002: Milestone 1 Full Profile & Evidence Models
"""
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
        ("documents", "0001_initial"),
    ]

    operations = [
        # Alter Profile fields to match Milestone 1 specification
        migrations.AlterModelOptions(
            name="profile",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Professional Profile",
                "verbose_name_plural": "Professional Profiles",
            },
        ),
        migrations.AddField(
            model_name="profile",
            name="city",
            field=models.CharField(blank=True, help_text="City of residence.", max_length=100),
        ),
        migrations.AddField(
            model_name="profile",
            name="phone",
            field=models.CharField(blank=True, help_text="Contact telephone / mobile number.", max_length=50),
        ),
        migrations.AddField(
            model_name="profile",
            name="personal_website_url",
            field=models.URLField(blank=True, help_text="Personal website or blog URL."),
        ),
        migrations.AddField(
            model_name="profile",
            name="availability",
            field=models.CharField(
                choices=[
                    ("AVAILABLE", "Available Immediately"),
                    ("OPEN_TO_OPPORTUNITIES", "Open to Opportunities"),
                    ("EMPLOYED", "Employed / Exploring Selectively"),
                    ("NOT_AVAILABLE", "Not Available"),
                ],
                default="AVAILABLE",
                help_text="Current availability status for opportunities.",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="remote_preference",
            field=models.CharField(
                choices=[
                    ("REMOTE_ONLY", "Remote Only"),
                    ("HYBRID", "Hybrid"),
                    ("ONSITE", "On-site"),
                    ("FLEXIBLE", "Flexible"),
                ],
                default="FLEXIBLE",
                help_text="Work arrangement preference.",
                max_length=50,
            ),
        ),

        # Create Skill
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("name", models.CharField(db_index=True, help_text="Skill name (e.g. Python, Google Earth Engine, QGIS, PyTorch).", max_length=150)),
                ("category", models.CharField(choices=[("TECHNICAL", "Technical"), ("GEOSPATIAL", "Geospatial"), ("REMOTE_SENSING", "Remote Sensing"), ("SOFTWARE", "Software Engineering"), ("DATA", "Data Science & Analytics"), ("AI_ML", "AI & Machine Learning"), ("CLIMATE", "Climate & Earth Observation"), ("AGRICULTURE", "Agriculture & Food Systems"), ("RESEARCH", "Research & Methodology"), ("BUSINESS", "Business & Strategy"), ("LEADERSHIP", "Leadership & Management"), ("COMMUNICATION", "Communication & Writing"), ("OTHER", "Other")], default="TECHNICAL", max_length=50)),
                ("proficiency", models.CharField(choices=[("BEGINNER", "Beginner"), ("INTERMEDIATE", "Intermediate"), ("ADVANCED", "Advanced"), ("EXPERT", "Expert")], default="INTERMEDIATE", max_length=30)),
                ("years_experience", models.DecimalField(blank=True, decimal_places=1, help_text="Estimated years of practical experience with this skill.", max_digits=4, null=True)),
                ("description", models.TextField(blank=True, help_text="Specific contextual details, tools, or projects where this skill was applied.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="skills", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Skill",
                "verbose_name_plural": "Skills",
                "ordering": ["category", "name"],
                "unique_together": {("profile", "name")},
            },
        ),

        # Create Experience
        migrations.CreateModel(
            name="Experience",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("organization", models.CharField(db_index=True, help_text="Company, institution, or organization name.", max_length=255)),
                ("position", models.CharField(db_index=True, help_text="Job title or role.", max_length=255)),
                ("employment_type", models.CharField(choices=[("FULL_TIME", "Full-time"), ("PART_TIME", "Part-time"), ("CONTRACT", "Contract"), ("INTERNSHIP", "Internship"), ("FREELANCE", "Freelance"), ("CONSULTING", "Consulting"), ("VOLUNTEER", "Volunteer"), ("FOUNDER", "Founder"), ("OTHER", "Other")], default="FULL_TIME", max_length=50)),
                ("location", models.CharField(blank=True, help_text="Location of work (or Remote).", max_length=255)),
                ("start_date", models.DateField(help_text="Role start date.")),
                ("end_date", models.DateField(blank=True, help_text="Role end date (leave empty if current).", null=True)),
                ("is_current", models.BooleanField(default=False, help_text="Check if you currently hold this position.")),
                ("description", models.TextField(blank=True, help_text="Core responsibilities and duties.")),
                ("achievements", models.TextField(blank=True, help_text="Key achievements, metrics, and measurable outcomes.")),
                ("url", models.URLField(blank=True, help_text="Organization website or project verification link.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="experiences", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Experience",
                "verbose_name_plural": "Experiences",
                "ordering": ["-is_current", "-start_date"],
            },
        ),

        # Create Education
        migrations.CreateModel(
            name="Education",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("institution", models.CharField(db_index=True, help_text="University, college, or academic institution name.", max_length=255)),
                ("degree", models.CharField(help_text="Degree or credential (e.g. Bachelor of Science, Master of Science).", max_length=255)),
                ("field_of_study", models.CharField(help_text="Field of study or major (e.g. Geomatics Engineering, Computer Science).", max_length=255)),
                ("location", models.CharField(blank=True, help_text="Institution city, country.", max_length=255)),
                ("start_date", models.DateField(help_text="Start date of studies.")),
                ("end_date", models.DateField(blank=True, help_text="Graduation / completion date (leave blank if ongoing).", null=True)),
                ("is_current", models.BooleanField(default=False, help_text="Check if you are currently enrolled.")),
                ("description", models.TextField(blank=True, help_text="Relevant coursework, academic honors, or thesis topic.")),
                ("grade", models.CharField(blank=True, help_text="GPA, honors classification, or grading result (optional).", max_length=100)),
                ("url", models.URLField(blank=True, help_text="Institution or program verification link.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="education", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Education Record",
                "verbose_name_plural": "Education Records",
                "ordering": ["-is_current", "-start_date"],
            },
        ),

        # Create Project
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("name", models.CharField(db_index=True, help_text="Project title.", max_length=255)),
                ("category", models.CharField(choices=[("GEOSPATIAL", "Geospatial & Remote Sensing"), ("EARTH_OBSERVATION", "Earth Observation & Satellite"), ("CLIMATE", "Climate & Environment"), ("AGRICULTURE", "Agriculture & Precision Farming"), ("SOFTWARE", "Software & Systems Architecture"), ("AI", "Artificial Intelligence & ML"), ("RESEARCH", "Scientific & Applied Research"), ("COMMUNITY", "Open Source & Community"), ("ENTREPRENEURSHIP", "Entrepreneurship & Commercial"), ("OTHER", "Other")], default="GEOSPATIAL", max_length=50)),
                ("role", models.CharField(blank=True, help_text="Your role (e.g. Lead Developer, Principal Investigator).", max_length=150)),
                ("technologies", models.CharField(blank=True, help_text="Comma-separated tools & stacks (e.g. Python, Sentinel-2, GDAL, Django, Docker).", max_length=500)),
                ("description", models.TextField(help_text="Clear factual summary of project scope, problem tackled, and technical approach.")),
                ("impact", models.TextField(blank=True, help_text="Measurable results, user adoption, publications, or practical outcomes.")),
                ("start_date", models.DateField(blank=True, help_text="Project start date.", null=True)),
                ("end_date", models.DateField(blank=True, help_text="Completion date (leave empty if ongoing).", null=True)),
                ("is_current", models.BooleanField(default=False, help_text="Check if this project is actively ongoing.")),
                ("url", models.URLField(blank=True, help_text="Live demonstration or production system URL.")),
                ("repository_url", models.URLField(blank=True, help_text="Public GitHub or GitLab repository URL.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="projects", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
                "ordering": ["-is_current", "-start_date"],
            },
        ),

        # Create Achievement
        migrations.CreateModel(
            name="Achievement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("title", models.CharField(db_index=True, help_text="Award or recognition title (e.g. NASA Space Apps Winner, Copernicus Hackathon 1st Place).", max_length=255)),
                ("organization", models.CharField(help_text="Awarding institution or organizing body.", max_length=255)),
                ("date", models.DateField(blank=True, help_text="Date awarded or achieved.", null=True)),
                ("description", models.TextField(blank=True, help_text="Context of the achievement, selection criteria, or prize.")),
                ("url", models.URLField(blank=True, help_text="Official announcement, certificate link, or news release.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="achievements", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Achievement",
                "verbose_name_plural": "Achievements",
                "ordering": ["-date", "-created_at"],
            },
        ),

        # Create Certification
        migrations.CreateModel(
            name="Certification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("name", models.CharField(db_index=True, help_text="Certification title (e.g. AWS Certified Solutions Architect, GISP Certification).", max_length=255)),
                ("issuer", models.CharField(help_text="Issuing authority or body (e.g. Amazon Web Services, GISCI).", max_length=255)),
                ("credential_id", models.CharField(blank=True, help_text="License or credential ID.", max_length=255)),
                ("credential_url", models.URLField(blank=True, help_text="Verification link on the issuer's validation portal.")),
                ("issue_date", models.DateField(help_text="Date certification was issued.")),
                ("expiry_date", models.DateField(blank=True, help_text="Expiry date (leave blank if does not expire).", null=True)),
                ("description", models.TextField(blank=True, help_text="Summary of competencies or domains covered.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="certifications", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Certification",
                "verbose_name_plural": "Certifications",
                "ordering": ["-issue_date"],
            },
        ),

        # Create Publication
        migrations.CreateModel(
            name="Publication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("title", models.CharField(help_text="Publication title.", max_length=300)),
                ("publication_type", models.CharField(choices=[("JOURNAL", "Journal Article"), ("CONFERENCE", "Conference Paper"), ("PREPRINT", "Preprint (arXiv/EarthArXiv)"), ("TECHNICAL_REPORT", "Technical Report"), ("ARTICLE", "Article / Technical Monograph"), ("THESIS", "Thesis / Dissertation"), ("BOOK", "Book / Book Chapter"), ("OTHER", "Other")], default="JOURNAL", max_length=50)),
                ("publisher", models.CharField(blank=True, help_text="Publisher, journal name, or conference proceeding.", max_length=255)),
                ("authors", models.CharField(blank=True, help_text="Author list as published (e.g. Mwoha, H., Smith, J.).", max_length=500)),
                ("publication_date", models.DateField(blank=True, help_text="Publication or release date.", null=True)),
                ("doi", models.CharField(blank=True, help_text="Digital Object Identifier (DOI).", max_length=150)),
                ("url", models.URLField(blank=True, help_text="Link to published paper, PDF, or DOI landing page.")),
                ("description", models.TextField(blank=True, help_text="Abstract or brief summary of findings.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="publications", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Publication",
                "verbose_name_plural": "Publications",
                "ordering": ["-publication_date", "-created_at"],
            },
        ),

        # Create Language
        migrations.CreateModel(
            name="Language",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("language", models.CharField(help_text="Language name (e.g. English, Swahili, French).", max_length=100)),
                ("proficiency", models.CharField(choices=[("BASIC", "Basic / Elementary"), ("CONVERSATIONAL", "Conversational"), ("PROFESSIONAL", "Professional Working"), ("FLUENT", "Full Professional / Fluent"), ("NATIVE", "Native / Bilingual")], default="PROFESSIONAL", max_length=50)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="languages", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Language",
                "verbose_name_plural": "Languages",
                "ordering": ["language"],
                "unique_together": {("profile", "language")},
            },
        ),

        # Create ProfilePreference
        migrations.CreateModel(
            name="ProfilePreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("target_opportunity_types", models.JSONField(blank=True, default=list, help_text="Target opportunity types (e.g. Jobs, Fellowships, Grants, Accelerators, Research).")),
                ("target_sectors", models.JSONField(blank=True, default=list, help_text="Target industry sectors (e.g. Geospatial, Earth Observation, Climate, Agriculture, AI).")),
                ("work_modes", models.JSONField(blank=True, default=list, help_text="Target work modes (Remote, Hybrid, On-site).")),
                ("target_countries", models.CharField(blank=True, help_text="Comma-separated countries of interest (e.g. Kenya, United States, United Kingdom, Global).", max_length=500)),
                ("target_regions", models.CharField(blank=True, help_text="Target regions (e.g. East Africa, Sub-Saharan Africa, North America, Europe, Global).", max_length=500)),
                ("min_compensation", models.CharField(blank=True, help_text="Minimum desired compensation or grant threshold (optional).", max_length=150)),
                ("additional_notes", models.TextField(blank=True, help_text="Any additional explicit constraints or preferences for opportunity evaluation.")),
                ("profile", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="preferences", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Profile Preference",
                "verbose_name_plural": "Profile Preferences",
            },
        ),

        # Create ProfileVersion
        migrations.CreateModel(
            name="ProfileVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("version", models.PositiveIntegerField(help_text="Monotonically increasing version number.")),
                ("change_summary", models.CharField(help_text="Brief description of what was changed or updated.", max_length=255)),
                ("snapshot_data", models.JSONField(blank=True, default=dict, help_text="Structured snapshot payload of profile state at this version.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Profile Version",
                "verbose_name_plural": "Profile Versions",
                "ordering": ["-version"],
                "unique_together": {("profile", "version")},
            },
        ),

        # Create Evidence
        migrations.CreateModel(
            name="Evidence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("evidence_type", models.CharField(choices=[("CV", "Curriculum Vitae / Resume"), ("CERTIFICATE", "Official Certificate"), ("PROJECT", "Project Demonstration"), ("GITHUB_REPOSITORY", "Code Repository (GitHub/GitLab)"), ("PORTFOLIO", "Portfolio Item"), ("PUBLICATION", "Academic / Technical Publication"), ("AWARD", "Award / Competition Win"), ("EMPLOYMENT", "Employment Verification"), ("EDUCATION", "Academic Degree / Transcript"), ("REFERENCE", "Reference / Recommendation"), ("OTHER", "Other Source")], db_index=True, default="PROJECT", max_length=50)),
                ("title", models.CharField(help_text="Clear title of what this evidence proves (e.g. GitHub: FloodRisk-Sentinel Pipeline).", max_length=255)),
                ("claim_summary", models.TextField(blank=True, help_text="The specific professional claim or competency this evidence substantiates.")),
                ("description", models.TextField(blank=True, help_text="Factual explanation of the evidence, methodology, or context.")),
                ("source_url", models.URLField(blank=True, help_text="Direct verifiable link (GitHub repo, published paper, live app, certification verify URL).")),
                ("verified", models.BooleanField(default=False, help_text="Mark True if verified against primary documentation, URL, or official record.")),
                ("verification_notes", models.TextField(blank=True, help_text="Audit notes on how this evidence was verified.")),
                ("document", models.ForeignKey(blank=True, help_text="Optional attached document from your Document Vault supporting this claim.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="supporting_evidence", to="documents.document")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evidence_items", to="profiles.profile")),
                ("related_achievement", models.ForeignKey(blank=True, help_text="Associated Achievement record.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evidence_records", to="profiles.achievement")),
                ("related_certification", models.ForeignKey(blank=True, help_text="Associated Certification record.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evidence_records", to="profiles.certification")),
                ("related_education", models.ForeignKey(blank=True, help_text="Associated Education record.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evidence_records", to="profiles.education")),
                ("related_experience", models.ForeignKey(blank=True, help_text="Associated Experience record.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evidence_records", to="profiles.experience")),
                ("related_project", models.ForeignKey(blank=True, help_text="Associated Project record.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evidence_records", to="profiles.project")),
            ],
            options={
                "verbose_name": "Evidence Item",
                "verbose_name_plural": "Evidence Bank",
                "ordering": ["-verified", "-created_at"],
            },
        ),
    ]
