"""
MwohaOS Matching Initial Migration — Milestone 4: Opportunity Alignment & Recommendations
"""
import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
        ("opportunities", "0003_intelligence_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="OpportunityMatch",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("match_status", models.CharField(choices=[("PENDING", "Pending"), ("PROCESSING", "Processing"), ("COMPLETED", "Completed"), ("PARTIAL", "Partial"), ("FAILED", "Failed"), ("STALE", "Stale")], db_index=True, default="PENDING", max_length=50)),
                ("overall_score", models.FloatField(db_index=True, default=0.0, help_text="Weighted match score (0-100). Never an AI black-box guarantee.")),
                ("eligibility_status", models.CharField(choices=[("ELIGIBLE", "Eligible"), ("INELIGIBLE", "Ineligible"), ("UNCERTAIN", "Uncertain"), ("NOT_ASSESSED", "Not Assessed")], db_index=True, default="NOT_ASSESSED", max_length=50)),
                ("eligibility_confidence", models.FloatField(default=0.0, help_text="Confidence of eligibility assessment (0.0 to 1.0).")),
                ("eligibility_reasons", models.JSONField(blank=True, default=list, help_text="Factual reasons explaining eligibility or ineligibility determination.")),
                ("skill_score", models.FloatField(default=0.0)),
                ("experience_score", models.FloatField(default=0.0)),
                ("education_score", models.FloatField(default=0.0)),
                ("preference_score", models.FloatField(default=0.0)),
                ("location_score", models.FloatField(default=0.0)),
                ("opportunity_type_score", models.FloatField(default=0.0)),
                ("sector_score", models.FloatField(default=0.0)),
                ("required_requirements_met", models.JSONField(blank=True, default=list, help_text="List of mandatory requirements satisfied by profile evidence.")),
                ("required_requirements_missing", models.JSONField(blank=True, default=list, help_text="List of mandatory requirements with no evidence in profile.")),
                ("required_requirements_uncertain", models.JSONField(blank=True, default=list, help_text="Requirements that cannot be evaluated due to insufficient data.")),
                ("preferred_requirements_met", models.JSONField(blank=True, default=list, help_text="List of bonus/preferred requirements satisfied.")),
                ("preferred_requirements_missing", models.JSONField(blank=True, default=list, help_text="List of preferred requirements not found in profile.")),
                ("matching_skills", models.JSONField(blank=True, default=list, help_text="List of skill matches with match_type (EXACT, NORMALIZED, RELATED) and evidence.")),
                ("missing_skills", models.JSONField(blank=True, default=list, help_text="Required skills missing from profile.")),
                ("uncertain_skills", models.JSONField(blank=True, default=list, help_text="Skills that are ambiguous or lack proficiency indicators.")),
                ("matching_experience", models.JSONField(blank=True, default=list, help_text="Traceable links to Profile Experience records meeting requirements.")),
                ("matching_projects", models.JSONField(blank=True, default=list, help_text="Traceable links to Profile Project/Evidence records demonstrating required skills.")),
                ("evidence_summary", models.JSONField(blank=True, default=list, help_text="Structured claims and foreign references linking requirements to profile facts.")),
                ("strengths", models.JSONField(blank=True, default=list, help_text="Key competitive strengths identified from profile facts.")),
                ("gaps", models.JSONField(blank=True, default=list, help_text="Identified qualification or documentation gaps.")),
                ("explanation", models.TextField(blank=True, help_text="Comprehensive, factual human-readable explanation of why this matches or gaps exist.")),
                ("confidence", models.FloatField(default=0.85, help_text="Assessment confidence score (0.0 to 1.0).")),
                ("matching_version", models.CharField(default="1.0", help_text="Algorithm version used to produce this match.", max_length=50)),
                ("profile_snapshot_hash", models.CharField(blank=True, help_text="SHA-256 hash of profile state at time of matching (stale detection).", max_length=64)),
                ("opportunity_snapshot_hash", models.CharField(blank=True, help_text="SHA-256 hash of opportunity content at time of matching.", max_length=64)),
                ("intelligence_snapshot_hash", models.CharField(blank=True, help_text="SHA-256 hash of opportunity intelligence at time of matching.", max_length=64)),
                ("ai_used", models.BooleanField(default=False)),
                ("ai_provider", models.CharField(blank=True, max_length=50)),
                ("ai_model", models.CharField(blank=True, max_length=100)),
                ("last_matched_at", models.DateTimeField(blank=True, null=True)),
                ("opportunity", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="profile_matches", to="opportunities.opportunity")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="opportunity_matches", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Opportunity Match",
                "verbose_name_plural": "Opportunity Matches",
                "ordering": ["-overall_score", "-created_at"],
                "unique_together": {("profile", "opportunity")},
                "indexes": [
                    models.Index(fields=["profile", "match_status"], name="matching_op_profile_85f6bb_idx"),
                    models.Index(fields=["profile", "eligibility_status"], name="matching_op_profile_1a5dbe_idx"),
                    models.Index(fields=["profile", "overall_score"], name="matching_op_profile_2174fc_idx"),
                    models.Index(fields=["last_matched_at"], name="matching_op_last_ma_3e3703_idx"),
                ],
            },
        ),
    ]
