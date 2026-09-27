"""
MwohaOS Management Command: update_application_readiness
Recalculates deterministic readiness scores and submission blocker validation for applications.
"""
from django.core.management.base import BaseCommand
from apps.applications.models import Application
from apps.applications.constants import ApplicationStatus
from apps.applications.services.readiness import evaluate_application_readiness


class Command(BaseCommand):
    help = "Recalculates application submission readiness scores and material completeness."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Evaluate all applications regardless of status.",
        )
        parser.add_argument(
            "--application",
            type=str,
            help="Evaluate a single application by UUID.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Limit number of applications processed.",
        )

    def handle(self, *args, **options):
        qs = Application.objects.all()

        if options["application"]:
            qs = qs.filter(pk=options["application"])
        elif not options["all"]:
            # Default to active/in-progress applications
            qs = qs.filter(
                status__in=[
                    ApplicationStatus.SAVED,
                    ApplicationStatus.PREPARING,
                    ApplicationStatus.READY_FOR_REVIEW,
                    ApplicationStatus.READY_TO_SUBMIT,
                ]
            )

        limit = options.get("limit", 50)
        apps = list(qs.select_related("opportunity")[:limit])
        count = len(apps)

        self.stdout.write(f"Evaluating readiness for {count} applications...")
        ready_count = 0

        for app in apps:
            result = evaluate_application_readiness(app, save=True)
            if result["is_ready_to_submit"]:
                ready_count += 1
            self.stdout.write(
                f"  - App {app.id} ({app.display_title[:30]}): Score {result['readiness_score']}% (Ready: {result['is_ready_to_submit']})"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed readiness evaluation for {count} applications. {ready_count} marked ready to submit."
            )
        )
