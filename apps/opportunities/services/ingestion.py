"""
MwohaOS Ingestion Pipeline Orchestrator — Milestone 2
Executes the standard pipeline:
SOURCE → FETCH → PARSE → NORMALIZE → VALIDATE → DEDUPLICATE → STORE
Creates an IngestionRun audit record with statistics.
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from apps.opportunities.models import OpportunitySource, IngestionRun, Opportunity
from apps.opportunities.constants import IngestionStatus, OpportunityStatus
from .base_connector import BaseOpportunityConnector
from .connectors import get_connector_for_source
from .validation import store_or_update_opportunity, OpportunityValidationError

logger = logging.getLogger("mwohaos.ingestion")


class IngestionPipeline:
    """
    Orchestrates opportunity ingestion for a given source or connector.
    """

    def process_source(self, source: OpportunitySource) -> IngestionRun:
        """
        Runs discovery pipeline for an OpportunitySource.
        """
        if not source.enabled:
            logger.info(f"Skipping disabled source '{source.name}'.")
            run = IngestionRun.objects.create(
                source=source,
                status=IngestionStatus.SUCCESS,
                error_message="Skipped (source is disabled).",
                completed_at=timezone.now(),
            )
            return run

        connector = get_connector_for_source(source)
        return self.process_connector(connector, source=source)

    def process_connector(
        self,
        connector: BaseOpportunityConnector,
        source: Optional[OpportunitySource] = None,
    ) -> IngestionRun:
        """
        Runs discovery pipeline for any connector instance.
        """
        if not source and connector.source_obj:
            source = connector.source_obj

        # Create running audit record
        run = IngestionRun.objects.create(
            source=source,
            status=IngestionStatus.RUNNING,
            started_at=timezone.now(),
        )

        items_fetched = 0
        items_parsed = 0
        items_created = 0
        items_updated = 0
        items_skipped = 0
        items_failed = 0
        error_msg = ""

        try:
            # 1. FETCH
            raw_payload = connector.fetch()
            items_fetched = 1

            # 2. PARSE
            candidates = connector.parse(raw_payload)
            items_parsed = len(candidates)

            # 3. NORMALIZE → VALIDATE → DEDUPLICATE → STORE
            for candidate in candidates:
                try:
                    norm_payload = connector.normalize(candidate)
                    _, created = store_or_update_opportunity(norm_payload, source_obj=source)
                    if created:
                        items_created += 1
                    else:
                        items_updated += 1
                except OpportunityValidationError as val_err:
                    items_skipped += 1
                    logger.debug(f"Candidate skipped due to validation: {val_err}")
                except Exception as item_err:
                    items_failed += 1
                    logger.warning(f"Failed to process candidate item: {item_err}")

            run.status = IngestionStatus.SUCCESS if items_failed == 0 else IngestionStatus.PARTIAL

        except Exception as e:
            error_msg = str(e)
            run.status = IngestionStatus.FAILED
            logger.error(f"Ingestion pipeline failed for source '{source.name if source else 'connector'}': {e}", exc_info=True)

        finally:
            now = timezone.now()
            run.completed_at = now
            run.items_fetched = items_fetched
            run.items_parsed = items_parsed
            run.items_created = items_created
            run.items_updated = items_updated
            run.items_skipped = items_skipped
            run.items_failed = items_failed
            run.error_message = error_msg
            run.save()

            if source:
                source.last_run = now
                if run.status in (IngestionStatus.SUCCESS, IngestionStatus.PARTIAL):
                    source.last_success = now
                if error_msg:
                    source.last_error = error_msg
                source.save(update_fields=["last_run", "last_success", "last_error", "updated_at"])

        return run


def expire_stale_opportunities() -> int:
    """
    Deterministic maintenance task: marks past-deadline opportunities as EXPIRED.
    Does not delete them (retains for future career analytics).
    Returns count of updated records.
    """
    now = timezone.now()
    updated = Opportunity.objects.filter(
        status=OpportunityStatus.ACTIVE,
        deadline__lt=now,
    ).update(status=OpportunityStatus.EXPIRED)
    return updated
