"""
MwohaOS Matching Views — Milestone 4: Recommendations Dashboard & Match Detail
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from apps.opportunities.models import Opportunity
from apps.opportunities.constants import OpportunityType, Sector
from apps.matching.models import OpportunityMatch
from apps.matching.constants import EligibilityStatus, MatchStatus
from apps.matching.services.recommendation import get_relevant_opportunities
from apps.matching.services.matcher import match_profile_opportunity
from apps.matching.tasks import match_opportunity_task


@login_required
def matching_dashboard_view(request):
    """
    Matching Dashboard: Displays ranked, explainable opportunities for the authenticated user.
    """
    profile = getattr(request.user, "profile", None)
    if not profile:
        messages.warning(request, "Please set up your profile first to view opportunity matches.")
        return redirect("profiles:overview")

    # Filters
    min_score_str = request.GET.get("min_score", "0")
    try:
        min_score = float(min_score_str)
    except ValueError:
        min_score = 0.0

    eligibility = request.GET.get("eligibility", "")
    opp_type = request.GET.get("type", "")
    sector = request.GET.get("sector", "")
    remote_param = request.GET.get("remote", "")
    ordering = request.GET.get("order", "-overall_score")

    remote_bool = None
    if remote_param == "1":
        remote_bool = True
    elif remote_param == "0":
        remote_bool = False

    matches_qs = get_relevant_opportunities(
        profile=profile,
        min_score=min_score,
        eligibility_status=eligibility if eligibility else None,
        opportunity_type=opp_type if opp_type else None,
        sector=sector if sector else None,
        remote=remote_bool,
        ordering=ordering,
    )

    paginator = Paginator(matches_qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Calculate summary metrics for user's dashboard header
    total_matched = OpportunityMatch.objects.filter(profile=profile, match_status=MatchStatus.COMPLETED).count()
    eligible_count = OpportunityMatch.objects.filter(profile=profile, eligibility_status=EligibilityStatus.ELIGIBLE).count()
    high_match_count = OpportunityMatch.objects.filter(profile=profile, overall_score__gte=80.0).count()

    context = {
        "page_obj": page_obj,
        "total_matched": total_matched,
        "eligible_count": eligible_count,
        "high_match_count": high_match_count,
        "min_score": min_score_str,
        "selected_eligibility": eligibility,
        "selected_type": opp_type,
        "selected_sector": sector,
        "remote": remote_param,
        "ordering": ordering,
        "eligibility_choices": EligibilityStatus.choices,
        "opportunity_types": OpportunityType.choices,
        "sectors": Sector.choices,
    }
    return render(request, "matching/matches.html", context)


@login_required
def match_detail_view(request, pk):
    """
    Detailed Match Breakdown:
    Comprehensive, explainable breakdown showing:
      - Overall score & Score band
      - Eligibility analysis & reasoning
      - Component scores (skills, experience, education, preferences)
      - Requirements met vs missing
      - Traceable evidence from user profile
      - Gaps & recommendations
    """
    profile = get_object_or_404(request.user.profile.__class__, user=request.user)
    match_record = get_object_or_404(
        OpportunityMatch.objects.select_related(
            "opportunity",
            "opportunity__intelligence",
            "opportunity__source",
            "profile",
        ),
        pk=pk,
        profile=profile,  # Strict user ownership
    )

    return render(
        request,
        "matching/match_detail.html",
        {
            "match": match_record,
            "opportunity": match_record.opportunity,
            "intelligence": getattr(match_record.opportunity, "intelligence", None),
        },
    )


@login_required
@require_POST
def rematch_opportunity_view(request, pk):
    """
    Forces immediate on-demand re-calculation of the match for an opportunity.
    """
    profile = get_object_or_404(request.user.profile.__class__, user=request.user)
    opp = get_object_or_404(Opportunity, pk=pk)
    match_record = match_profile_opportunity(profile, opp, force_refresh=True)
    messages.success(request, f"Match recalculated for '{opp.title}'. Score: {match_record.overall_score:.0f}%.")
    return redirect("matching:detail", pk=match_record.pk)
