"""
MwohaOS Applications Initial Migration — Milestone 5: Application Workspace
"""
import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
import apps.applications.models
import apps.documents.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
        ("opportunities", "0001_initial"),
        ("matching", "0001_initial"),
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("SAVED", "Saved / Considering"), ("PREPARING", "Preparing Materials"), ("READY_FOR_REVIEW", "Ready for Final Review"), ("READY_TO_SUBMIT", "Ready to Submit"), ("SUBMITTED", "Submitted"), ("UNDER_REVIEW", "Under Review"), ("INTERVIEWING", "Interviewing / Assessment"), ("OFFERED", "Offered / Accepted"), ("REJECTED", "Not Selected"), ("WITHDRAWN", "Withdrawn"), ("ARCHIVED", "Archived")], db_index=True, default="SAVED", max_length=50)),
                ("priority", models.CharField(choices=[("LOW", "Low Priority"), ("MEDIUM", "Medium Priority"), ("HIGH", "High Priority"), ("URGENT", "Urgent / Immediate")], db_index=True, default="MEDIUM", max_length=50)),
                ("custom_title", models.CharField(blank=True, help_text="Custom title override for internal tracking (defaults to opportunity title).", max_length=255)),
                ("custom_organization", models.CharField(blank=True, help_text="Custom organization override.", max_length=255)),
                ("strategy_notes", models.TextField(blank=True, help_text="Personal positioning strategy, narrative angle, or research findings.")),
                ("portal_url", models.URLField(blank=True, help_text="Official application submission portal URL.", max_length=1000)),
                ("target_submission_date", models.DateField(blank=True, help_text="Personal target completion date (defaults to opportunity deadline).", null=True)),
                ("readiness_score", models.PositiveSmallIntegerField(default=0, help_text="Deterministic readiness score (0-100) based on materials, questions, and review.")),
                ("is_ready_to_submit", models.BooleanField(default=False, help_text="True when all mandatory documents and questions are completed.")),
                ("user_review_completed", models.BooleanField(default=False, help_text="Explicit user signoff before final submission.")),
                ("user_review_notes", models.TextField(blank=True, help_text="Candidate signoff comments or final review notes.")),
                ("user_reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("submission_method", models.CharField(blank=True, choices=[("PORTAL", "Online Application Portal"), ("EMAIL", "Email Submission"), ("MANUAL_FORM", "Web Form"), ("DIRECT", "Direct Upload / API"), ("OTHER", "Other Submission Channel")], default="PORTAL", max_length=50)),
                ("submission_confirmation_code", models.CharField(blank=True, help_text="Confirmation number, receipt reference, or application ID.", max_length=255)),
                ("submission_notes", models.TextField(blank=True, help_text="Submission confirmation receipt details, portal message, or verification notes.")),
                ("match", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="applications", to="matching.opportunitymatch")),
                ("opportunity", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="opportunities.opportunity")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Application",
                "verbose_name_plural": "Applications",
                "ordering": ["-updated_at"],
                "unique_together": {("profile", "opportunity")},
            },
        ),
        migrations.CreateModel(
            name="ApplicationActivity",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("activity_type", models.CharField(choices=[("CREATED", "Workspace Created"), ("STATUS_CHANGE", "Stage Changed"), ("PRIORITY_CHANGE", "Priority Updated"), ("DOCUMENT_ATTACHED", "Document Attached"), ("DOCUMENT_REMOVED", "Document Removed"), ("QUESTION_UPDATED", "Question Response Updated"), ("REVIEW_SIGNED_OFF", "User Review Signed Off"), ("SUBMISSION_RECORDED", "Submission Recorded"), ("NOTE_ADDED", "Note Added")], default="STATUS_CHANGE", max_length=50)),
                ("from_status", models.CharField(blank=True, max_length=50)),
                ("to_status", models.CharField(blank=True, max_length=50)),
                ("description", models.TextField()),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activities", to="applications.application")),
            ],
            options={
                "verbose_name": "Application Activity",
                "verbose_name_plural": "Application Activities",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ApplicationNote",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(blank=True, max_length=200)),
                ("category", models.CharField(choices=[("GENERAL", "General Notes"), ("RESEARCH", "Organization & Opportunity Research"), ("CONTACT", "Key Contacts & Outreach"), ("INTERVIEW_PREP", "Interview Preparation"), ("FEEDBACK", "Reviewer / Recruiter Feedback")], default="GENERAL", max_length=50)),
                ("content", models.TextField()),
                ("is_pinned", models.BooleanField(default=False)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notes", to="applications.application")),
            ],
            options={
                "verbose_name": "Application Note",
                "verbose_name_plural": "Application Notes",
                "ordering": ["-is_pinned", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ApplicationQuestion",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("question_text", models.TextField(help_text="The prompt or question asked in the application.")),
                ("category", models.CharField(choices=[("MOTIVATION", "Motivation & Fit"), ("TECHNICAL", "Technical Expertise"), ("EXPERIENCE", "Experience & Background"), ("LEADERSHIP", "Leadership & Impact"), ("PROJECT", "Project Proposal"), ("LOGISTICS", "Logistics & Compensation"), ("OTHER", "General / Other")], default="MOTIVATION", max_length=50)),
                ("order", models.PositiveSmallIntegerField(default=0, help_text="Order in the application questionnaire.")),
                ("is_required", models.BooleanField(default=True, help_text="Whether answering this question is required for submission.")),
                ("max_words", models.PositiveIntegerField(blank=True, help_text="Maximum allowed words (optional).", null=True)),
                ("max_characters", models.PositiveIntegerField(blank=True, help_text="Maximum allowed characters (optional).", null=True)),
                ("answer_draft", models.TextField(blank=True, help_text="Candidate answer draft.")),
                ("status", models.CharField(choices=[("NOT_STARTED", "Not Started"), ("IN_PROGRESS", "Drafting"), ("READY_FOR_REVIEW", "Draft Ready"), ("FINAL", "Finalized")], db_index=True, default="NOT_STARTED", max_length=50)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="applications.application")),
            ],
            options={
                "verbose_name": "Application Question",
                "verbose_name_plural": "Application Questions",
                "ordering": ["order", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="ApplicationDocument",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("document_role", models.CharField(choices=[("CV", "Curriculum Vitae (CV)"), ("RESUME", "Resume"), ("COVER_LETTER", "Cover Letter / Letter of Intent"), ("TRANSCRIPT", "Academic Transcript"), ("PORTFOLIO", "Portfolio / Work Samples"), ("CERTIFICATE", "Certificate / Accreditation"), ("PROPOSAL", "Project Proposal / Concept Note"), ("RECOMMENDATION", "Letter of Recommendation"), ("IDENTIFICATION", "Identification / Passport"), ("OTHER", "Other Attachment")], db_index=True, default="CV", max_length=50)),
                ("title", models.CharField(help_text="Label for this document (e.g. 'Targeted 2-Page CV', 'Cover Letter Draft').", max_length=255)),
                ("is_required", models.BooleanField(default=True, help_text="Whether this document is mandatory for application submission.")),
                ("is_tailored", models.BooleanField(default=False, help_text="Flag indicating this document was specifically customized for this opportunity.")),
                ("tailored_notes", models.TextField(blank=True, help_text="Summary of customizations made to tailor this document for the role.")),
                ("status", models.CharField(choices=[("MISSING", "Required / Missing"), ("DRAFT", "Draft in Progress"), ("ATTACHED", "Attached & Ready"), ("VERIFIED", "Verified & Checked")], db_index=True, default="ATTACHED", max_length=50)),
                ("file", models.FileField(blank=True, help_text="Optional dedicated file uploaded specifically for this application.", null=True, upload_to=apps.applications.models.application_upload_path, validators=[apps.documents.models.validate_document_file])),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="application_documents", to="applications.application")),
                ("document", models.ForeignKey(blank=True, help_text="Linked document from the user's Document Vault.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="application_usages", to="documents.document")),
            ],
            options={
                "verbose_name": "Application Document",
                "verbose_name_plural": "Application Documents",
                "ordering": ["-is_required", "created_at"],
            },
        ),
    ]
