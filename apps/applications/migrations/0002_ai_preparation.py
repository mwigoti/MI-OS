"""
MwohaOS Applications Migration 0002 — Milestone 6: AI Preparation
Adds versioned application document iterations, question draft revisions, and CV tailoring models.
"""
import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationdocument",
            name="content",
            field=models.TextField(
                blank=True,
                help_text="Tailored document text or markdown (e.g. for generated cover letters or tailored CV text).",
            ),
        ),
        migrations.AlterField(
            model_name="applicationactivity",
            name="activity_type",
            field=models.CharField(
                choices=[
                    ("CREATED", "Workspace Created"),
                    ("STATUS_CHANGE", "Stage Changed"),
                    ("PRIORITY_CHANGE", "Priority Updated"),
                    ("DOCUMENT_ATTACHED", "Document Attached"),
                    ("DOCUMENT_REMOVED", "Document Removed"),
                    ("QUESTION_UPDATED", "Question Response Updated"),
                    ("REVIEW_SIGNED_OFF", "User Review Signed Off"),
                    ("SUBMISSION_RECORDED", "Submission Recorded"),
                    ("NOTE_ADDED", "Note Added"),
                    ("AI_GENERATION", "AI Preparation Generated"),
                    ("AI_APPLIED", "AI Draft Applied"),
                ],
                default="STATUS_CHANGE",
                max_length=50,
            ),
        ),
        migrations.CreateModel(
            name="ApplicationDocumentVersion",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("version_number", models.PositiveIntegerField(default=1)),
                ("title", models.CharField(blank=True, max_length=255)),
                ("content", models.TextField(help_text="Tailored document text or markdown.")),
                ("tailoring_notes", models.TextField(blank=True, help_text="Notes on how this draft was tailored.")),
                ("grounding_evidence", models.JSONField(blank=True, default=list, help_text="Traceable citations of profile experiences, skills, and projects used in this version.")),
                ("provider", models.CharField(default="DETERMINISTIC", max_length=50)),
                ("model", models.CharField(blank=True, max_length=100)),
                ("token_metrics", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("application_document", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="applications.applicationdocument")),
            ],
            options={
                "verbose_name": "Application Document Version",
                "verbose_name_plural": "Application Document Versions",
                "ordering": ["-version_number", "-created_at"],
                "unique_together": {("application_document", "version_number")},
            },
        ),
        migrations.CreateModel(
            name="QuestionDraftVersion",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("version_number", models.PositiveIntegerField(default=1)),
                ("tone", models.CharField(choices=[("STAR_METHOD", "STAR Method (Situation, Task, Action, Result)"), ("CONCISE", "Concise & Direct"), ("EXECUTIVE", "Executive & Strategic"), ("ACADEMIC", "Academic & Research-Oriented")], default="STAR_METHOD", max_length=50)),
                ("answer_text", models.TextField()),
                ("word_count", models.PositiveIntegerField(default=0)),
                ("char_count", models.PositiveIntegerField(default=0)),
                ("grounding_evidence", models.JSONField(blank=True, default=list, help_text="Profile evidence citations incorporated into this answer.")),
                ("provider", models.CharField(default="DETERMINISTIC", max_length=50)),
                ("model", models.CharField(blank=True, max_length=100)),
                ("token_metrics", models.JSONField(blank=True, default=dict)),
                ("is_selected", models.BooleanField(default=False)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="draft_versions", to="applications.applicationquestion")),
            ],
            options={
                "verbose_name": "Question Draft Version",
                "verbose_name_plural": "Question Draft Versions",
                "ordering": ["-version_number", "-created_at"],
                "unique_together": {("question", "version_number")},
            },
        ),
        migrations.CreateModel(
            name="CVTailoringResult",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("targeted_summary", models.TextField(blank=True, help_text="Targeted professional summary emphasizing opportunity alignment.")),
                ("prioritized_skills", models.JSONField(blank=True, default=list, help_text="Skills ordered by relevance to requirements with match explanations.")),
                ("tailored_experience_bullets", models.JSONField(blank=True, default=list, help_text="Accomplishment bullet points enhanced with action verbs and metrics.")),
                ("selected_projects", models.JSONField(blank=True, default=list, help_text="Recommended projects highlighting target proficiencies.")),
                ("ats_keyword_coverage", models.JSONField(blank=True, default=dict, help_text="ATS keyword match statistics: coverage percentage, found keywords, missing keywords.")),
                ("provider", models.CharField(default="DETERMINISTIC", max_length=50)),
                ("model", models.CharField(blank=True, max_length=100)),
                ("token_metrics", models.JSONField(blank=True, default=dict)),
                ("application", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="cv_tailoring", to="applications.application")),
            ],
            options={
                "verbose_name": "CV Tailoring Result",
                "verbose_name_plural": "CV Tailoring Results",
            },
        ),
    ]
