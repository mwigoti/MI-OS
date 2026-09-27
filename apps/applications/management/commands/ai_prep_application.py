"""
MwohaOS Management Command: ai_prep_application — Milestone 6: AI Preparation
Generates tailored cover letters, CV optimizations, and essay question answers
grounded in verified candidate profile evidence.
"""
from django.core.management.base import BaseCommand, CommandError
from apps.applications.models import Application
from apps.applications.constants import AITone
from apps.applications.services.ai_prep import (
    generate_tailored_cover_letter,
    generate_cv_tailoring,
    AIPreparationService,
)


class Command(BaseCommand):
    help = "Generates AI tailored materials (cover letter, CV optimizations, essay questions) for an application."

    def add_arguments(self, parser):
        parser.add_argument(
            "--application",
            type=str,
            required=True,
            help="Application UUID to prepare materials for.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Execute complete preparation pass (Cover letter, CV tailoring, and question answers).",
        )
        parser.add_argument(
            "--cover-letter",
            action="store_true",
            help="Generate tailored cover letter.",
        )
        parser.add_argument(
            "--cv",
            action="store_true",
            help="Generate CV tailoring and ATS keyword alignment.",
        )
        parser.add_argument(
            "--questions",
            action="store_true",
            help="Draft answers for all required application questions.",
        )
        parser.add_argument(
            "--tone",
            type=str,
            default=AITone.STAR_METHOD,
            choices=[choice[0] for choice in AITone.choices],
            help="Drafting framework or tone (STAR_METHOD, CONCISE, EXECUTIVE, ACADEMIC).",
        )
        parser.add_argument(
            "--deterministic",
            action="store_true",
            help="Force deterministic offline rule-based generation.",
        )

    def handle(self, *args, **options):
        app_id = options["application"]
        try:
            app = Application.objects.select_related("profile", "opportunity").get(pk=app_id)
        except Application.DoesNotExist:
            raise CommandError(f"Application with ID '{app_id}' does not exist.")

        self.stdout.write(f"Initiating AI Preparation for: {app.display_title} ({app.display_organization})")

        do_all = options["all"] or not (options["cover_letter"] or options["cv"] or options["questions"])
        tone = options["tone"]
        det = options["deterministic"]

        if do_all:
            self.stdout.write("Running full AI preparation suite...")
            res = AIPreparationService.prepare_full_application(app, tone=tone, force_deterministic=det)
            self.stdout.write(self.style.SUCCESS(f"Full preparation complete. Updated readiness: {res['final_readiness_score']}%."))
            return

        if options["cover_letter"]:
            self.stdout.write("Generating tailored cover letter...")
            cl_res = generate_tailored_cover_letter(app, tone=tone, force_deterministic=det)
            self.stdout.write(self.style.SUCCESS(
                f"Cover letter generated (v{cl_res['version_number']}). "
                f"Grounded in {cl_res['grounding_count']} profile citations. "
                f"Readiness: {cl_res['readiness_score']}%."
            ))

        if options["cv"]:
            self.stdout.write("Generating CV tailoring and ATS keyword alignment...")
            cv_res = generate_cv_tailoring(app, update_cv_document=True, force_deterministic=det)
            ats = cv_res.get("ats_keyword_coverage", {})
            self.stdout.write(self.style.SUCCESS(
                f"CV tailoring complete. ATS Coverage: {ats.get('coverage_score', 0)}%. "
                f"Readiness: {cv_res['readiness_score']}%."
            ))

        if options["questions"]:
            self.stdout.write("Drafting answers for required questions...")
            for q in app.questions.filter(is_required=True):
                q_res = AIPreparationService.prepare_full_application(app, tone=tone, force_deterministic=det)
            self.stdout.write(self.style.SUCCESS("All required questions drafted."))
