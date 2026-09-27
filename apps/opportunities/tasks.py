"""
MwohaOS Opportunities Celery Tasks — Milestone 2
Provides idempotent background tasks for source polling, single opportunity processing,
and automated expiration of overdue opportunities.
"""
import logging
from celery import shared_task
from django.utils import timezone
from apps.opportunities.models import OpportunitySource
from apps.opportunities.services.ingestion import IngestionPipeline, expire_stale_opportunities

logger = logging.getLogger("mwohaos.tasks")


@shared_task(name="apps.opportunities.tasks.discover_all_opportunities", bind=True, max_retries=2)
def discover_all_opportunities(self):
    """
    Periodic task: polls all enabled OpportunitySources sequentially.
    Ensures a failure in one source does NOT prevent subsequent sources from executing.
    """
    logger.info("Starting opportunity discovery across all enabled sources...")
    pipeline = IngestionPipeline()
    sources = OpportunitySource.objects.filter(enabled=True)

    summary = {
        "sources_run": 0,
        "total_created": 0,
        "total_updated": 0,
        "failed_sources": 0,
    }

    for source in sources:
        try:
            logger.info(f"Executing discovery for source: {source.name} ({source.slug})")
            run = pipeline.process_source(source)
            summary["sources_run"] += 1
            summary["total_created"] += run.items_created
            summary["total_updated"] += run.items_updated
            if run.status == "FAILED":
                summary["failed_sources"] += 1
        except Exception as e:
            summary["failed_sources"] += 1
            logger.error(f"Unexpected error running source {source.name}: {e}", exc_info=True)

    logger.info(f"Opportunity discovery completed: {summary}")
    return summary


@shared_task(name="apps.opportunities.tasks.refresh_opportunity_source", bind=True, max_retries=1)
def refresh_opportunity_source(self, source_id: str):
    """
    Idempotent task: refreshes a specific OpportunitySource on demand.
    """
    try:
        source = OpportunitySource.objects.get(id=source_id)
        pipeline = IngestionPipeline()
        run = pipeline.process_source(source)
        return {
            "status": run.status,
            "created": run.items_created,
            "updated": run.items_updated,
            "error": run.error_message,
        }
    except OpportunitySource.DoesNotExist:
        logger.error(f"Source with id {source_id} not found.")
        return {"status": "FAILED", "error": "Source not found."}


@shared_task(name="apps.opportunities.tasks.expire_past_opportunities")
def expire_past_opportunities():
    """
    Periodic maintenance task: marks past-deadline opportunities as EXPIRED.
    """
    count = expire_stale_opportunities()
    logger.info(f"Marked {count} opportunities as expired.")
    return {"expired_count": count}


@shared_task(name="apps.opportunities.tasks.extract_opportunity_intelligence_task", bind=True, max_retries=2)
def extract_opportunity_intelligence_task(self, opportunity_id: str, force: bool = False):
    """
    Asynchronous, retryable task to process intelligence for a single Opportunity.
    """
    from apps.opportunities.models import Opportunity
    from apps.opportunities.services.intelligence import process_opportunity_intelligence

    try:
        opp = Opportunity.objects.get(id=opportunity_id)
        intel = process_opportunity_intelligence(opp, force_refresh=force)
        return {
            "opportunity_id": str(opp.id),
            "status": intel.extraction_status,
            "method": intel.extraction_method,
            "provider": intel.extraction_provider,
            "confidence": intel.confidence,
        }
    except Opportunity.DoesNotExist:
        logger.error(f"Opportunity {opportunity_id} not found for intelligence processing.")
        return {"error": "Not found"}
    except Exception as e:
        logger.error(f"Intelligence processing task failed for {opportunity_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=10)


@shared_task(name="apps.opportunities.tasks.process_pending_intelligence")
def process_pending_intelligence():
    """
    Scheduled batch task to process pending opportunities up to batch limit.
    Ensures free API quotas are preserved and never oversubscribed.
    """
    from django.conf import settings
    from apps.opportunities.models import Opportunity
    from apps.opportunities.constants import ExtractionStatus
    from apps.opportunities.services.intelligence import process_opportunity_intelligence

    batch_size = getattr(settings, "OPPORTUNITY_INTELLIGENCE_BATCH_SIZE", 10)
    # Find opportunities with no intelligence, or PENDING or FAILED
    pending_opps = (
        Opportunity.objects.filter(
            intelligence__isnull=True
        )
        .order_by("-created_at")[:batch_size]
    )

    if not pending_opps.exists():
        # Check if any have status PENDING
        pending_opps = (
            Opportunity.objects.filter(
                intelligence__extraction_status=ExtractionStatus.PENDING
            )
            .order_by("-created_at")[:batch_size]
        )

    processed = 0
    for opp in pending_opps:
        try:
            process_opportunity_intelligence(opp)
            processed += 1
        except Exception as e:
            logger.error(f"Error in batch intelligence processing for {opp.id}: {e}")

    logger.info(f"Processed {processed} pending opportunities for intelligence.")
    return {"processed_count": processed}

