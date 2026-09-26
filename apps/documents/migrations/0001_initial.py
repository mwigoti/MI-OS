"""
MwohaOS Documents Initial Migration
"""
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
import apps.documents.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("title", models.CharField(help_text="Descriptive title (e.g. 2026 Geospatial CV, AWS Solutions Architect Certificate).", max_length=255)),
                ("document_type", models.CharField(choices=[("CV", "Curriculum Vitae (CV)"), ("RESUME", "Resume"), ("CERTIFICATE", "Certificate / License"), ("TRANSCRIPT", "Academic Transcript"), ("PORTFOLIO", "Portfolio / Work Sample"), ("REFERENCE", "Letter of Recommendation / Reference"), ("COVER_LETTER", "Cover Letter"), ("PUBLICATION", "Publication / Paper"), ("AWARD", "Award Notice"), ("IDENTIFICATION", "Identification Document"), ("OTHER", "Other Document")], db_index=True, default="CV", max_length=50)),
                ("file", models.FileField(help_text="Supported: PDF, DOCX, TXT, PNG, JPG (max 10MB).", upload_to=apps.documents.models.document_upload_path, validators=[apps.documents.models.validate_document_file])),
                ("description", models.TextField(blank=True, help_text="Notes on this document, target audience, or specific revisions.")),
                ("version", models.CharField(default="1.0", help_text="Version identifier (e.g. 1.0, 2026-Q1, Tech-Focused).", max_length=50)),
                ("is_primary", models.BooleanField(default=False, help_text="Mark as the default / primary document for this category.")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="profiles.profile")),
            ],
            options={
                "verbose_name": "Document",
                "verbose_name_plural": "Documents",
                "ordering": ["-is_primary", "-created_at"],
            },
        ),
    ]
