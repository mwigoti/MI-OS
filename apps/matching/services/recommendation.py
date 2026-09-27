"""
MwohaOS Recommendation & Query Service — Milestone 4
Filters, orders, and formats matched opportunities for user presentation.
Never invents scores; reads directly from OpportunityMatch truth.
"""
from typing import Optional, List
from django.db.models import QuerySet
from apps.profiles.models import Profile
from apps.matching.models import OpportunityMatch
from apps.matching.constants import MatchStatus, EligibilityStatus


def get_relevant_opportunities(
    profile: Profile,
    min_score: float = 0.0,
    eligibility_status: Optional[str] = None,
    opportunity_type: Optional[str] = None,
    sector: Optional[str] = None,
    remote: Optional[bool] = None,
    status: str = "COMPLETED",
    ordering: str = "-overall_score",
) -> QuerySet[OpportunityMatch]:
    """
    Returns filtered and sorted opportunity matches for a user's profile.
    """
    qs = (
        OpportunityMatch.objects.filter(profile=profile)
        .select_related("opportunity", "opportunity__source", "opportunity__intelligence")
    )

    if status:
        qs = qs.filter(match_status=status)

    if min_score > 0.0:
        qs = qs.filter(overall_score__gte=min_score)

    if eligibility_status:
        qs = qs.filter(eligibility_status=eligibility_status)

    if opportunity_type:
        qs = qs.filter(opportunity__opportunity_type=opportunity_type)

    if sector:
        qs = qs.filter(opportunity__sector=sector)

    if remote is not None:
        qs = qs.filter(opportunity__remote=remote)

    # Valid orderings
    valid_orderings = {
        "-overall_score": "-overall_score",
        "overall_score": "overall_score",
        "deadline_soonest": "opportunity__deadline",
        "-created_at": "-created_at",
        "-last_matched_at": "-last_matched_at",
    }
    order_field = valid_orderings.get(ordering, "-overall_score")
    return qs.order_by(order_field)
