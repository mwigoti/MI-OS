"""
MwohaOS Deterministic Manual Opportunity URL Ingestion — Milestone 2
Extracts metadata from HTML public pages (Title, Meta Description, OpenGraph, JSON-LD)
without using AI. Sanitizes HTML and applies SSRF security checks.
"""
import json
import logging
import re
from typing import Dict, Any
from urllib.parse import urlparse
from .http_client import HttpClient
from .security import validate_public_url, sanitize_html
from .normalization import normalize_whitespace, parse_flexible_datetime
from apps.opportunities.constants import OpportunityType, Sector

logger = logging.getLogger("mwohaos.manual_ingestion")


def extract_metadata_from_url(target_url: str) -> Dict[str, Any]:
    """
    Fetches the public webpage, verifies SSRF safety, and extracts:
    - HTML <title>
    - <meta name="description"> or og:description
    - og:title, og:site_name
    - JSON-LD structured data (JobPosting, Event, etc.)
    - Estimated organization, opportunity type, and sector
    """
    validate_public_url(target_url)

    client = HttpClient(timeout=15, max_retries=2)
    response = client.get(target_url)
    html = response.text

    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc.replace("www.", "")

    title = ""
    description = ""
    organization = domain.split(".")[0].capitalize()
    location = ""
    posted_date = None
    deadline = None
    compensation = ""

    # 1. Extract JSON-LD structured data
    json_ld_matches = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    for raw_json in json_ld_matches:
        try:
            data = json.loads(raw_json.strip())
            items = data if isinstance(data, list) else [data]
            for it in items:
                schema_type = str(it.get("@type", "")).lower()
                if "jobposting" in schema_type or "event" in schema_type or "opportunity" in schema_type:
                    title = it.get("title", "") or title
                    description = it.get("description", "") or description
                    hiring_org = it.get("hiringOrganization", {})
                    if isinstance(hiring_org, dict) and hiring_org.get("name"):
                        organization = hiring_org.get("name")
                    elif isinstance(hiring_org, str):
                        organization = hiring_org

                    posted_date = it.get("datePosted")
                    deadline = it.get("validThrough")
                    break
        except Exception:
            pass

    # 2. Extract OpenGraph and standard Meta tags
    if not title:
        og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if og_title:
            title = og_title.group(1)

    if not title:
        page_title = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if page_title:
            title = page_title.group(1)

    if not description:
        og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if og_desc:
            description = og_desc.group(1)

    if not description:
        meta_desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if meta_desc:
            description = meta_desc.group(1)

    # 3. Detect Organization from og:site_name if available
    og_site = re.search(r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if og_site and og_site.group(1):
        organization = og_site.group(1)

    # 4. Deterministic type guessing based on title keywords
    t_lower = (title or "").lower()
    opp_type = OpportunityType.JOB
    if "fellowship" in t_lower:
        opp_type = OpportunityType.FELLOWSHIP
    elif "grant" in t_lower or "funding" in t_lower:
        opp_type = OpportunityType.GRANT
    elif "scholarship" in t_lower:
        opp_type = OpportunityType.SCHOLARSHIP
    elif "hackathon" in t_lower:
        opp_type = OpportunityType.HACKATHON
    elif "competition" in t_lower or "challenge" in t_lower:
        opp_type = OpportunityType.COMPETITION
    elif "internship" in t_lower or "intern" in t_lower:
        opp_type = OpportunityType.INTERNSHIP
    elif "research" in t_lower or "phd" in t_lower or "postdoc" in t_lower:
        opp_type = OpportunityType.RESEARCH
    elif "conference" in t_lower or "symposium" in t_lower:
        opp_type = OpportunityType.CONFERENCE

    # 5. Deterministic sector guessing
    sector = Sector.GENERAL
    if any(k in t_lower for k in ["geospatial", "gis", "remote sensing", "earth observation", "satellite", "radar"]):
        sector = Sector.GEOSPATIAL
    elif any(k in t_lower for k in ["climate", "weather", "carbon", "environment"]):
        sector = Sector.CLIMATE
    elif any(k in t_lower for k in ["software", "developer", "engineer", "full stack", "backend"]):
        sector = Sector.SOFTWARE
    elif any(k in t_lower for k in ["ai", "machine learning", "deep learning", "nlp"]):
        sector = Sector.AI

    return {
        "title": normalize_whitespace(title),
        "organization": normalize_whitespace(organization),
        "description": sanitize_html(description),
        "source_url": target_url,
        "application_url": target_url,
        "opportunity_type": opp_type,
        "sector": sector,
        "location": location,
        "posted_date": posted_date,
        "deadline": deadline,
        "compensation": compensation,
        "raw_content": html[:10000],
    }
