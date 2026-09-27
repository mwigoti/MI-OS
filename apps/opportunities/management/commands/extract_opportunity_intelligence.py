"""
MwohaOS Management Command: extract_opportunity_intelligence — Milestone 3
Allows processing pending opportunities or analyzing a specific opportunity by UUID.
Options:
  --pending: process pending unanalyzed opportunities up to --limit
  --opportunity <uuid>: process single opportunity
  --limit <n>: batch limit (default from settings)
  --force: bypass caching and re-run extraction
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.opportunities.models import Opportunity
from apps.opportunities.constants import ExtractionStatus
from apps.opportunities.services.intelligence import process_opportunity_intelligence


class Command(BaseCommand):
    help = "Extracts structured opportunity intelligence using deterministic baseline + hosted AI providers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pending",
            action="store_true",
            help="Process batch of pending opportunities.",
        )
        parser.add_argument(
            "--opportunity",
            type=str,
            help="UUID of a specific Opportunity to analyze.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=getattr(settings, "OPPORTUNITY_INTELLIGENCE_BATCH_SIZE", 10),
            help="Max opportunities to process in pending batch.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-extraction even if intelligence already exists.",
        )

    def handle(self, *args, **options):
        opp_uuid = options.get("opportunity")
        is_pending = options.get("pending")
        limit = options.get("limit")
        force = options.get("force")

        if opp_uuid:
            try:
                opp = Opportunity.objects.get(id=opp_uuid)
            except Opportunity.DoesNotExist:
                raise CommandError(f"Opportunity with ID '{opp_uuid}' does not exist.")

            self.stdout.write(f"Processing intelligence for: {opp.title} ({opp.id})...")
            intel = process_opportunity_intelligence(opp, force_refresh=force)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Complete! Status: {intel.extraction_status}, Method: {intel.extraction_method}, "
                    f"Provider: {intel.extraction_provider}, Confidence: {intel.confidence}"
                )
            )
            return

        if is_pending:
            qs = (
                Opportunity.objects.filter(intelligence__isnull=True)
                .order_by("-created_at")[:limit]
            )
            if not qs.exists():
                qs = (
                    Opportunity.objects.filter(
                        intelligence__extraction_status=ExtractionStatus.PENDING
                    )
                    .order_by("-created_at")[:limit]
                )

            count = qs.count()
            self.stdout.write(f"Found {count} pending opportunities to process (limit: {limit}).")
            processed = 0
            for opp in qs:
                self.stdout.write(f"  -> Analyzing: {opp.title}...")
                intel = process_opportunity_intelligence(opp, force_refresh=force)
                self.stdout.write(
                    f"     Status: {intel.extraction_status} | Method: {intel.extraction_method} | Provider: {intel.extraction_provider}"
                )
                processed += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully processed {processed} opportunities."))
            return

        self.stdout.write(
            self.style.WARNING("Please specify either --opportunity <uuid> or --pending. Use --help for usage.")
        )
