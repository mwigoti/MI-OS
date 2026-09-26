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
