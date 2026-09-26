"""
MwohaOS Opportunities Selectors — Milestone 2: Query & Filter Logic
"""
from datetime import datetime
from typing import Optional, Dict, Any
from django.db.models import QuerySet, Q
from django.utils import timezone
from apps.opportunities.models import Opportunity
from apps.opportunities.constants import OpportunityStatus


def get_opportunities_queryset(
    query: str = "",
    opportunity_type: str = "",
    sector: str = "",
    country: str = "",
    remote: Optional[bool] = None,
    status: str = "",
    source_id: Optional[str] = None,
    deadline_filter: str = "",
    ordering: str = "-posted_date",
) -> QuerySet[Opportunity]:
    """
    Returns an optimized queryset for the Opportunity Inbox with full search,
    filters, and sorting.
    """
    qs = Opportunity.objects.select_related("source").all()

    # Search filter
    if query:
        query = query.strip()
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(organization__icontains=query) |
            Q(description__icontains=query) |
            Q(preferred_skills__icontains=query)
        )

    # Opportunity Type
    if opportunity_type:
        qs = qs.filter(opportunity_type=opportunity_type)

    # Sector
    if sector:
        qs = qs.filter(sector=sector)

    # Country
    if country:
        qs = qs.filter(country__icontains=country)

    # Remote
    if remote is not None:
        qs = qs.filter(remote=remote)

    # Status (Default: Active if not specified)
    if status:
        qs = qs.filter(status=status)
    else:
        qs = qs.filter(status=OpportunityStatus.ACTIVE)

    # Source
    if source_id:
        qs = qs.filter(source_id=source_id)

    # Deadline Filter
    now = timezone.now()
    if deadline_filter == "upcoming_7_days":
        seven_days = now + timezone.timedelta(days=7)
        qs = qs.filter(deadline__gte=now, deadline__lte=seven_days)
    elif deadline_filter == "upcoming_30_days":
        thirty_days = now + timezone.timedelta(days=30)
        qs = qs.filter(deadline__gte=now, deadline__lte=thirty_days)
    elif deadline_filter == "no_deadline":
        qs = qs.filter(deadline__isnull=True)

    # Ordering
    valid_orderings = {
        "-posted_date": "-posted_date",
        "posted_date": "posted_date",
        "deadline_soonest": "deadline",
        "-deadline": "-deadline",
        "-created_at": "-created_at",
        "title": "title",
    }
    order_field = valid_orderings.get(ordering, "-posted_date")
    return qs.order_by(order_field)
