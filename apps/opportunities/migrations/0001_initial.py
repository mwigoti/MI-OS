"""
MwohaOS Opportunities Initial Migration — Milestone 2: Discovery & Ingestion
"""
import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="OpportunitySource",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(help_text="Readable name of the source.", max_length=255, unique=True)),
                ("slug", models.SlugField(help_text="Unique connector identifier.", max_length=100, unique=True)),
                ("source_type", models.CharField(choices=[("RSS", "RSS / Atom Feed"), ("API", "Public API"), ("WEBSITE", "Structured Public Website"), ("CAREER_PAGE", "Organization Career Page"), ("JOB_BOARD", "Public Job Board"), ("MANUAL", "Manual Submission"), ("OTHER", "Other Connector")], default="RSS", help_text="Transport mechanism.", max_length=50)),
                ("base_url", models.URLField(help_text="Base feed or API endpoint URL.", max_length=500)),
                ("enabled", models.BooleanField(db_index=True, default=True, help_text="Toggle automated polling.")),
                ("configuration", models.JSONField(blank=True, default=dict, help_text="Connector-specific options (e.g. headers, default sector, opportunity type override).")),
                ("last_run", models.DateTimeField(blank=True, help_text="Timestamp of most recent run.", null=True)),
                ("last_success", models.DateTimeField(blank=True, help_text="Timestamp of most recent successful run.", null=True)),
                ("last_error", models.TextField(blank=True, help_text="Error message from last failure.")),
            ],
            options={
                "verbose_name": "Opportunity Source",
                "verbose_name_plural": "Opportunity Sources",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="IngestionRun",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("RUNNING", "Running"), ("SUCCESS", "Success"), ("PARTIAL", "Partial Success"), ("FAILED", "Failed")], db_index=True, default="RUNNING", max_length=50)),
                ("items_fetched", models.PositiveIntegerField(default=0)),
                ("items_parsed", models.PositiveIntegerField(default=0)),
                ("items_created", models.PositiveIntegerField(default=0)),
                ("items_updated", models.PositiveIntegerField(default=0)),
                ("items_skipped", models.PositiveIntegerField(default=0)),
                ("items_failed", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ingestion_runs", to="opportunities.opportunitysource")),
            ],
            options={
                "verbose_name": "Ingestion Run",
                "verbose_name_plural": "Ingestion Runs",
                "ordering": ["-started_at"],
            },
        ),
        migrations.CreateModel(
            name="Opportunity",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(db_index=True, help_text="Opportunity title.", max_length=500)),
                ("organization", models.CharField(db_index=True, help_text="Host company, university, or foundation.", max_length=255)),
                ("description", models.TextField(blank=True, help_text="Sanitized opportunity overview and context.")),
                ("opportunity_type", models.CharField(choices=[("JOB", "Job / Employment"), ("INTERNSHIP", "Internship"), ("FELLOWSHIP", "Fellowship"), ("GRANT", "Grant / Funding"), ("SCHOLARSHIP", "Scholarship"), ("COMPETITION", "Competition / Challenge"), ("HACKATHON", "Hackathon"), ("ACCELERATOR", "Accelerator"), ("INCUBATOR", "Incubator"), ("RESEARCH", "Research Position"), ("CONSULTING", "Consulting Engagement"), ("FREELANCE", "Freelance Project"), ("PROGRAM", "Training Program"), ("BOOTCAMP", "Bootcamp"), ("CONFERENCE", "Conference / Symposium"), ("OTHER", "Other Opportunity")], db_index=True, default="JOB", help_text="Primary category.", max_length=50)),
                ("sector", models.CharField(choices=[("GEOSPATIAL", "Geospatial & GIS"), ("REMOTE_SENSING", "Remote Sensing & Satellite Tech"), ("EARTH_OBSERVATION", "Earth Observation"), ("SPACE", "Space Systems"), ("CLIMATE", "Climate & Meteorology"), ("AGRICULTURE", "Agriculture & Food Security"), ("SOFTWARE", "Software Engineering"), ("AI", "Artificial Intelligence & ML"), ("DATA", "Data Science & Big Data"), ("RESEARCH", "Scientific Research"), ("ENGINEERING", "General Engineering"), ("ENTREPRENEURSHIP", "Entrepreneurship & Startups"), ("ENVIRONMENT", "Environment & Ecology"), ("DISASTER_RISK", "Disaster Risk & Emergency"), ("FINANCE", "Finance & Economics"), ("HEALTH", "Public Health & Biotech"), ("EDUCATION", "Education & Academics"), ("GENERAL", "General / Interdisciplinary"), ("OTHER", "Other Sector")], db_index=True, default="GENERAL", help_text="Domain focus.", max_length=50)),
                ("location", models.CharField(blank=True, help_text="City, region, or general location string.", max_length=255)),
                ("country", models.CharField(blank=True, db_index=True, help_text="Primary country.", max_length=100)),
                ("remote", models.BooleanField(db_index=True, default=False, help_text="Is remote participation/employment allowed?")),
                ("posted_date", models.DateTimeField(blank=True, help_text="Publication date from source.", null=True)),
                ("deadline", models.DateTimeField(blank=True, db_index=True, help_text="Application/submission deadline.", null=True)),
                ("deadline_timezone", models.CharField(blank=True, default="Africa/Nairobi", help_text="Timezone specified by source.", max_length=50)),
                ("source_url", models.URLField(db_index=True, help_text="Canonical source webpage or listing URL.", max_length=1000)),
                ("application_url", models.URLField(blank=True, help_text="Direct submission, portal, or registration link.", max_length=1000)),
                ("eligibility_text", models.TextField(blank=True, help_text="Eligibility parameters extracted from source.")),
                ("requirements", models.TextField(blank=True, help_text="Mandatory qualifications or requirements.")),
                ("preferred_skills", models.CharField(blank=True, help_text="Key skills mentioned in source.", max_length=500)),
                ("compensation", models.CharField(blank=True, help_text="Salary, grant amount, or prize funding.", max_length=255)),
                ("raw_content", models.TextField(blank=True, help_text="Raw payload or HTML extract preserved for audit & debug.")),
                ("content_hash", models.CharField(db_index=True, help_text="Deterministic SHA-256 hash of core content.", max_length=64)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("EXPIRED", "Expired"), ("CLOSED", "Closed / Filled"), ("ARCHIVED", "Archived")], db_index=True, default="ACTIVE", max_length=50)),
                ("first_seen_at", models.DateTimeField(default=django.utils.timezone.now, help_text="When first detected by MwohaOS.")),
                ("last_seen_at", models.DateTimeField(default=django.utils.timezone.now, help_text="When most recently re-observed.")),
                ("source", models.ForeignKey(blank=True, help_text="Origin source connector if automated.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="opportunities", to="opportunities.opportunitysource")),
            ],
            options={
                "verbose_name": "Opportunity",
                "verbose_name_plural": "Opportunities",
                "ordering": ["-posted_date", "-created_at"],
                "indexes": [
                    models.Index(fields=["status", "deadline"], name="opportuniti_status_ad82d9_idx"),
                    models.Index(fields=["organization", "title"], name="opportuniti_organiz_773957_idx"),
                ],
            },
        ),
    ]
