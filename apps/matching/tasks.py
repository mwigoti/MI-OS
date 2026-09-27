"""
MwohaOS Matching Celery Tasks — Milestone 4: Asynchronous & Scheduled Matching
Tasks are idempotent, bounded, and observable.
"""
import logging
from celery import shared_task
from django.conf import settings
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity
from apps.matching.models import OpportunityMatch
from apps.matching.services.matcher import match_profile_opportunity

logger = logging.getLogger("mwohaos.tasks")


@shared_task(name="apps.matching.tasks.match_opportunity_task", bind=True, max_retries=2)
def match_opportunity_task(self, profile_id: str, opportunity_id: str, force: bool = False):
    """
    Computes or updates an alignment match for a given profile and opportunity.
    """
    try:
        profile = Profile.objects.get(id=profile_id)
        opp = Opportunity.objects.get(id=opportunity_id)
        match_record = match_profile_opportunity(profile, opp, force_refresh=force)
        return {
            "match_id": str(match_record.id),
            "score": match_record.overall_score,
            "eligibility": match_record.eligibility_status,
            "status": match_record.match_status,
        }
    except Exception as e:
        logger.error(f"Task match_opportunity_task failed: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=10)


@shared_task(name="apps.matching.tasks.match_pending_opportunities")
def match_pending_opportunities(limit: int = 20):
    """
    Finds active opportunities not yet matched against user profiles and calculates alignment.
    Bounded to prevent performance bottlenecks.
    """
    profiles = Profile.objects.all()
    if not profiles.exists():
        return {"processed": 0, "message": "No profiles found."}

    # For personal agent paradigm, match active profiles against unmatched opportunities
    total_processed = 0
    for profile in profiles:
        # Find opportunities with no match record for this profile
        matched_opp_ids = OpportunityMatch.objects.filter(profile=profile).values_list("opportunity_id", flat=True)
        unmatched_opps = (
            Opportunity.objects.exclude(id__in=matched_opp_ids)
            .filter(status="ACTIVE")
            .order_by("-created_at")[:limit]
        )

        for opp in unmatched_opps:
            try:
                match_profile_opportunity(profile, opp)
                total_processed += 1
            except Exception as e:
                logger.error(f"Error matching opp {opp.id} for profile {profile.id}: {e}")

    logger.info(f"Processed {total_processed} pending opportunity matches.")
    return {"processed": total_processed}


@shared_task(name="apps.matching.tasks.rematch_stale_matches")
def rematch_stale_matches(limit: int = 20):
    """
    Finds matches flagged as STALE or where the underlying profile/opportunity has been modified.
    """
    stale_matches = OpportunityMatch.objects.filter(match_status="STALE")[:limit]
    count = 0
    for m in stale_matches:
        try:
            match_profile_opportunity(m.profile, m.opportunity, force_refresh=True)
            count += 1
        except Exception as e:
            logger.error(f"Failed to rematch stale match {m.id}: {e}")
    return {"rematched": count}


@shared_task(name="apps.matching.tasks.rematch_profile")
def rematch_profile(profile_id: str):
    """
    Recalculates all matches for a user when their profile credentials/preferences are updated.
    """
    try:
        profile = Profile.objects.get(id=profile_id)
        matches = OpportunityMatch.objects.filter(profile=profile)
        for m in matches:
            match_profile_opportunity(profile, m.opportunity, force_refresh=True)
        return {"profile_id": profile_id, "rematched_count": matches.count()}
    except Profile.DoesNotExist:
        return {"error": "Profile not found"}
