"""
MwohaOS Opportunities Migration 0003: OpportunityIntelligence & AIUsageLog Models (Milestone 3)
"""
import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("opportunities", "0002_seed_sources"),
    ]

    operations = [
        migrations.CreateModel(
            name="OpportunityIntelligence",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("summary", models.TextField(blank=True, help_text="Executive summary of the opportunity.")),
                ("organization_summary", models.TextField(blank=True, help_text="Background and mission of host entity.")),
                ("opportunity_purpose", models.TextField(blank=True, help_text="Objective, problem addressed, or goal.")),
                ("who_should_apply", models.JSONField(blank=True, default=list, help_text="Target applicant personas / demographics.")),
                ("responsibilities", models.JSONField(blank=True, default=list, help_text="Key duties, tasks, or project milestones.")),
                ("required_requirements", models.JSONField(blank=True, default=list, help_text="Mandatory qualifications / prerequisites.")),
                ("preferred_requirements", models.JSONField(blank=True, default=list, help_text="Bonus / nice-to-have qualifications.")),
                ("eligibility", models.JSONField(blank=True, default=dict, help_text="Structured eligibility parameters (nationality, education, etc.).")),
                ("required_documents", models.JSONField(blank=True, default=list, help_text="Document checklist (CV, Proposal, Letters, etc.).")),
                ("required_experience", models.JSONField(blank=True, default=list, help_text="Years of experience and domain track record.")),
                ("required_skills", models.JSONField(blank=True, default=list, help_text="Mandatory technical, domain, or soft skills.")),
                ("preferred_skills", models.JSONField(blank=True, default=list, help_text="Preferred / secondary skills.")),
                ("benefits", models.JSONField(blank=True, default=list, help_text="Funding, stipends, equity, mentoring, or perks.")),
                ("compensation_details", models.CharField(blank=True, help_text="Detailed compensation or prize structure.", max_length=500)),
                ("location_details", models.CharField(blank=True, help_text="Specific geographic or venue constraints.", max_length=500)),
                ("remote_details", models.CharField(blank=True, help_text="Remote policy (fully remote, timezones, hybrid).", max_length=500)),
                ("application_process", models.JSONField(blank=True, default=list, help_text="Step-by-step application workflow.")),
                ("important_dates", models.JSONField(blank=True, default=list, help_text="Key timeline events (opens, review, start date).")),
                ("application_instructions", models.JSONField(blank=True, default=list, help_text="Submission rules, portal links, or email guidelines.")),
                ("confidence", models.FloatField(default=0.0, help_text="Extraction confidence score (0.0 to 1.0). Never a fit/match score.")),
                ("extraction_status", models.CharField(choices=[("PENDING", "Pending"), ("PROCESSING", "Processing"), ("COMPLETED", "Completed"), ("PARTIAL", "Partial"), ("FAILED", "Failed")], db_index=True, default="PENDING", max_length=50)),
                ("extraction_method", models.CharField(choices=[("DETERMINISTIC", "Deterministic"), ("AI", "AI-Assisted"), ("HYBRID", "Hybrid"), ("MANUAL", "Manual")], default="DETERMINISTIC", max_length=50)),
                ("extraction_provider", models.CharField(choices=[("NONE", "None (Deterministic Only)"), ("GEMINI", "Google Gemini"), ("HUGGINGFACE", "Hugging Face Inference")], default="NONE", max_length=50)),
                ("model_name", models.CharField(blank=True, help_text="Exact LLM model name used.", max_length=100)),
                ("extraction_version", models.CharField(default="v1.0", help_text="Schema extraction version for cache invalidation.", max_length=50)),
                ("raw_extraction", models.JSONField(blank=True, default=dict, help_text="Full structured JSON returned by extraction engine.")),
                ("extraction_error", models.TextField(blank=True, help_text="Any error message encountered during analysis.")),
                ("last_extracted_at", models.DateTimeField(blank=True, null=True)),
                ("opportunity", models.OneToOneField(help_text="The opportunity analyzed.", on_delete=django.db.models.deletion.CASCADE, related_name="intelligence", to="opportunities.opportunity")),
            ],
            options={
                "verbose_name": "Opportunity Intelligence",
                "verbose_name_plural": "Opportunity Intelligence Records",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="AIUsageLog",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider", models.CharField(db_index=True, help_text="Provider used (gemini, huggingface).", max_length=50)),
                ("model", models.CharField(help_text="Model identifier.", max_length=100)),
                ("operation", models.CharField(default="extract_opportunity", max_length=100)),
                ("requested_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("success", models.BooleanField(default=False)),
                ("input_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("output_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("error_type", models.CharField(blank=True, max_length=100)),
                ("error_message", models.TextField(blank=True)),
                ("opportunity", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ai_usage_logs", to="opportunities.opportunity")),
            ],
            options={
                "verbose_name": "AI Usage Log",
                "verbose_name_plural": "AI Usage Logs",
                "ordering": ["-requested_at"],
            },
        ),
    ]
