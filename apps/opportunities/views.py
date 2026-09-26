"""
MwohaOS Opportunities Views — Milestone 2: Opportunity Inbox & Source Management
Provides:
  - Opportunity Inbox: paginated listings, search, multi-facet filtering, sorting
  - Opportunity Detail: clean distinction between source facts and normalized metadata
  - Manual URL Ingestion: 2-step extract-and-review workflow with SSRF protection
  - Source Management: overview of configured connectors, enable/disable toggle, manual trigger
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Opportunity, OpportunitySource, IngestionRun
from .constants import OpportunityType, Sector, OpportunityStatus, SourceType
from .selectors import get_opportunities_queryset
from .forms import ManualUrlIngestionForm, OpportunityEditForm
from .services.manual_ingestion import extract_metadata_from_url
from .services.normalization import normalize_opportunity_payload
from .services.validation import store_or_update_opportunity
from .tasks import refresh_opportunity_source


@login_required
def opportunity_inbox_view(request):
    """
    Opportunity Inbox: paginated list with real-time search, filters, and sorting.
    """
    query = request.GET.get("q", "").strip()
    opp_type = request.GET.get("type", "")
    sector = request.GET.get("sector", "")
    country = request.GET.get("country", "").strip()
    remote_param = request.GET.get("remote", "")
    status = request.GET.get("status", "ACTIVE")
    source_id = request.GET.get("source", "")
    deadline_filter = request.GET.get("deadline", "")
    ordering = request.GET.get("order", "-posted_date")

    remote_bool = None
    if remote_param == "1":
        remote_bool = True
    elif remote_param == "0":
        remote_bool = False

    opportunities_qs = get_opportunities_queryset(
        query=query,
        opportunity_type=opp_type,
        sector=sector,
        country=country,
        remote=remote_bool,
        status=status,
        source_id=source_id if source_id else None,
        deadline_filter=deadline_filter,
        ordering=ordering,
    )

    paginator = Paginator(opportunities_qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    sources = OpportunitySource.objects.all()

    context = {
        "page_obj": page_obj,
        "query": query,
        "selected_type": opp_type,
        "selected_sector": sector,
        "country": country,
        "remote": remote_param,
        "selected_status": status,
        "selected_source": source_id,
        "deadline_filter": deadline_filter,
        "ordering": ordering,
        "opportunity_types": OpportunityType.choices,
        "sectors": Sector.choices,
        "statuses": OpportunityStatus.choices,
        "sources": sources,
        "total_count": paginator.count,
    }
    return render(request, "opportunities/inbox.html", context)


@login_required
def opportunity_detail_view(request, pk):
    """
    Opportunity Detail view: structured representation clearly distinguishing
    primary source data from MwohaOS normalized metadata.
    """
    opportunity = get_object_or_404(Opportunity.objects.select_related("source"), pk=pk)
    return render(request, "opportunities/detail.html", {"opportunity": opportunity})


@login_required
def opportunity_manual_add_view(request):
    """
    Manual URL Ingestion:
    Step 1: Enter public URL -> Fetch & Extract Metadata without AI.
    Step 2: Review and edit normalized facts before saving.
    """
    initial_url = request.GET.get("url", "")
    if request.method == "POST":
        # Check if submitting the final edited form
        if "save_opportunity" in request.POST:
            form = OpportunityEditForm(request.POST)
            if form.is_valid():
                cleaned = form.cleaned_data
                norm_payload = normalize_opportunity_payload({
                    "title": cleaned["title"],
                    "organization": cleaned["organization"],
                    "description": cleaned["description"],
                    "opportunity_type": cleaned["opportunity_type"],
                    "sector": cleaned["sector"],
                    "location": cleaned["location"],
                    "country": cleaned["country"],
                    "remote": cleaned["remote"],
                    "deadline": cleaned["deadline"],
                    "deadline_timezone": cleaned["deadline_timezone"],
                    "source_url": cleaned["source_url"],
                    "application_url": cleaned["application_url"],
                    "eligibility_text": cleaned["eligibility_text"],
                    "requirements": cleaned["requirements"],
                    "preferred_skills": cleaned["preferred_skills"],
                    "compensation": cleaned["compensation"],
                })
                opp, created = store_or_update_opportunity(norm_payload)
                verb = "Created" if created else "Updated"
                messages.success(request, f"{verb} opportunity '{opp.title}'.")
                return redirect("opportunities:detail", pk=opp.pk)
            else:
                messages.error(request, "Please resolve form errors.")
                return render(request, "opportunities/manual_review.html", {"form": form})

        # Otherwise: Processing Step 1 URL extraction
        url_form = ManualUrlIngestionForm(request.POST)
        if url_form.is_valid():
            target_url = url_form.cleaned_data["target_url"]
            try:
                extracted = extract_metadata_from_url(target_url)
                # Populate review form
                review_form = OpportunityEditForm(initial={
                    "title": extracted.get("title", ""),
                    "organization": extracted.get("organization", ""),
                    "description": extracted.get("description", ""),
                    "source_url": extracted.get("source_url", ""),
                    "application_url": extracted.get("application_url", ""),
                    "opportunity_type": extracted.get("opportunity_type", OpportunityType.JOB),
                    "sector": extracted.get("sector", Sector.GENERAL),
                    "location": extracted.get("location", ""),
                    "compensation": extracted.get("compensation", ""),
                })
                messages.info(request, "Metadata extracted. Please review and refine the opportunity facts.")
                return render(request, "opportunities/manual_review.html", {
                    "form": review_form,
                    "target_url": target_url,
                })
            except Exception as e:
                messages.error(request, f"Failed to ingest URL: {e}")
    else:
        url_form = ManualUrlIngestionForm(initial={"target_url": initial_url} if initial_url else None)

    return render(request, "opportunities/manual_add.html", {"form": url_form})


@login_required
def sources_dashboard_view(request):
    """
    Source Management Console:
    View all discovery connectors, execution health, item counts, and manual run triggers.
    """
    sources = OpportunitySource.objects.all().prefetch_related("ingestion_runs")
    recent_runs = IngestionRun.objects.select_related("source").order_by("-started_at")[:10]

    return render(request, "opportunities/sources.html", {
        "sources": sources,
        "recent_runs": recent_runs,
    })


@login_required
@require_POST
def source_toggle_view(request, pk):
    """
    Enables or disables an opportunity source connector.
    """
    source = get_object_or_404(OpportunitySource, pk=pk)
    source.enabled = not source.enabled
    source.save(update_fields=["enabled", "updated_at"])
    state = "enabled" if source.enabled else "disabled"
    messages.success(request, f"Source '{source.name}' {state}.")
    return redirect("opportunities:sources")


@login_required
@require_POST
def source_trigger_view(request, pk):
    """
    Dispatches a Celery background task to poll the selected source immediately.
    """
    source = get_object_or_404(OpportunitySource, pk=pk)
    refresh_opportunity_source.delay(str(source.id))
    messages.success(request, f"Discovery triggered in background for '{source.name}'. Check ingestion log below.")
    return redirect("opportunities:sources")
