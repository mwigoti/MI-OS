# Generated initial migration for apps.profiles
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text="Timestamp when this record was created (timezone-aware).")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Timestamp when this record was last modified (timezone-aware).")),
                ("headline", models.CharField(blank=True, help_text="Professional title or headline.", max_length=255)),
                ("professional_summary", models.TextField(blank=True, help_text="Concise summary of professional background and target opportunities.")),
                ("location", models.CharField(blank=True, help_text="City, State / Region.", max_length=255)),
                ("country", models.CharField(blank=True, help_text="Primary country of residence.", max_length=100)),
                ("linkedin_url", models.URLField(blank=True, help_text="LinkedIn profile URL.")),
                ("github_url", models.URLField(blank=True, help_text="GitHub profile URL.")),
                ("portfolio_url", models.URLField(blank=True, help_text="Personal portfolio or website URL.")),
                ("work_authorization", models.CharField(blank=True, help_text="Work authorization status (e.g. Citizen, Permanent Resident, Visa).", max_length=255)),
                ("remote_preference", models.CharField(blank=True, choices=[("remote_only", "Remote Only"), ("hybrid", "Hybrid"), ("onsite", "On-site"), ("flexible", "Flexible")], default="flexible", help_text="Work arrangement preference.", max_length=50)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
    ]
