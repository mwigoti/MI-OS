"""
MwohaOS Deterministic Validation & Deduplication Service — Milestone 2
1. Validation: Ensures required fields (title, organization, source_url) are present and non-empty.
2. Deduplication: Three-tier deterministic resolution:
   - Priority 1: Canonical Source URL
   - Priority 2: Stable Content Hash
   - Priority 3: Organization + Normalized Title + Deadline
"""
import logging
from typing import Dict, Any, Tuple, Optional
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.opportunities.models import Opportunity
from apps.opportunities.constants import OpportunityStatus

logger = logging.getLogger("mwohaos.deduplication")


class OpportunityValidationError(ValidationError):
    """Raised when an opportunity record lacks essential factual identity."""
    pass


def validate_normalized_opportunity(payload: Dict[str, Any]) -> None:
    """
    Validates required fields.
    Required:
      - title (non-empty, >= 3 chars)
      - organization (non-empty)
      - source_url (valid url format)
    """
    title = payload.get("title", "")
    if not title or len(str(title).strip()) < 3:
        raise OpportunityValidationError("Opportunity title is missing or too short.")

    org = payload.get("organization", "")
    if not org or len(str(org).strip()) < 1:
        raise OpportunityValidationError("Host organization is required.")

    source_url = payload.get("source_url", "")
    if not source_url or not str(source_url).startswith(("http://", "https://")):
        raise OpportunityValidationError("Valid source URL starting with http:// or https:// is required.")


def resolve_deduplication(
    payload: Dict[str, Any],
    source_obj: Optional[Any] = None,
) -> Tuple[Optional[Opportunity], str]:
    """
    Deterministic deduplication resolver.
    Returns (existing_opportunity, match_strategy) or (None, 'NEW').

    Match Strategy Priorities:
      1. CANONICAL_URL
      2. CONTENT_HASH
      3. ORG_TITLE_DEADLINE
    """
    source_url = payload.get("source_url")
    content_hash = payload.get("content_hash")
    org = payload.get("organization")
    title = payload.get("title")
    deadline = payload.get("deadline")

    # Priority 1: Match on Canonical Source URL
    if source_url:
        match_by_url = Opportunity.objects.filter(source_url=source_url).first()
        if match_by_url:
            return match_by_url, "CANONICAL_URL"

    # Priority 2: Match on Content Hash
    if content_hash:
        match_by_hash = Opportunity.objects.filter(content_hash=content_hash).first()
        if match_by_hash:
            return match_by_hash, "CONTENT_HASH"

    # Priority 3: Match on Organization + Exact Title + (Optional Deadline)
    if org and title:
        qs = Opportunity.objects.filter(
            organization__iexact=org.strip(),
            title__iexact=title.strip(),
        )
        if deadline:
            qs = qs.filter(deadline=deadline)
        match_by_org_title = qs.first()
        if match_by_org_title:
            return match_by_org_title, "ORG_TITLE_DEADLINE"

    return None, "NEW"


def store_or_update_opportunity(
    payload: Dict[str, Any],
    source_obj: Optional[Any] = None,
) -> Tuple[Opportunity, bool]:
    """
    Saves a normalized opportunity into the database.
    If a duplicate is found via 3-tier matching, updates existing record fields
    and updates `last_seen_at`. If new, creates fresh Opportunity record.
    Returns (opportunity, created_bool).
    """
    validate_normalized_opportunity(payload)
    existing_opp, strategy = resolve_deduplication(payload, source_obj)

    now = timezone.now()

    # Determine status if expired
    status = OpportunityStatus.ACTIVE
    deadline = payload.get("deadline")
    if deadline and deadline < now:
        status = OpportunityStatus.EXPIRED

    if existing_opp:
        # Update existing record
        existing_opp.last_seen_at = now
        # Update mutable fields if new payload has content
        if payload.get("description") and len(payload["description"]) > len(existing_opp.description or ""):
            existing_opp.description = payload["description"]
        if payload.get("application_url"):
            existing_opp.application_url = payload["application_url"]
        if payload.get("deadline"):
            existing_opp.deadline = payload["deadline"]
        if payload.get("compensation"):
            existing_opp.compensation = payload["compensation"]
        if payload.get("eligibility_text"):
            existing_opp.eligibility_text = payload["eligibility_text"]

        # If previously active but deadline passed, mark expired
        if existing_opp.deadline and existing_opp.deadline < now:
            existing_opp.status = OpportunityStatus.EXPIRED

        existing_opp.save()
        return existing_opp, False

    # Create new Opportunity
    opp = Opportunity.objects.create(
        title=payload["title"],
        organization=payload["organization"],
        description=payload.get("description", ""),
        opportunity_type=payload.get("opportunity_type", "JOB"),
        sector=payload.get("sector", "GENERAL"),
        location=payload.get("location", ""),
        country=payload.get("country", ""),
        remote=payload.get("remote", False),
        posted_date=payload.get("posted_date"),
        deadline=payload.get("deadline"),
        deadline_timezone=payload.get("deadline_timezone", "Africa/Nairobi"),
        source=source_obj,
        source_url=payload["source_url"],
        application_url=payload.get("application_url", ""),
        eligibility_text=payload.get("eligibility_text", ""),
        requirements=payload.get("requirements", ""),
        preferred_skills=payload.get("preferred_skills", ""),
        compensation=payload.get("compensation", ""),
        raw_content=payload.get("raw_content", ""),
        content_hash=payload.get("content_hash", ""),
        status=status,
        first_seen_at=now,
        last_seen_at=now,
    )
    return opp, True
