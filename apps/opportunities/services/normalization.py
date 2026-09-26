"""
MwohaOS Deterministic Normalization Service — Milestone 2
Sanitizes strings, extracts canonical URLs, calculates stable content hashes,
and parses dates into timezone-aware datetimes.
Zero AI or heuristic guessing.
"""
from datetime import datetime, timezone as py_timezone
from email.utils import parsedate_to_datetime
import hashlib
import re
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from django.utils import timezone
from .security import sanitize_html

TRACKING_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "fbclid", "gclid", "msclkid", "mc_cid", "mc_eid", "source",
}


def normalize_whitespace(text: str) -> str:
    """Normalizes excessive spaces, tabs, and newlines."""
    if not text:
        return ""
    # Strip carriage returns and replace multi-spaces with single space
    cleaned = re.sub(r"[ \t]+", " ", str(text))
    # Replace 3+ newlines with 2
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def normalize_url(url: str) -> str:
    """
    Produces a canonical URL by removing marketing tracking parameters,
    normalizing scheme/host casing, and trimming whitespace.
    """
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path
        if not path:
            path = "/"

        # Filter tracking params
        query_dict = parse_qs(parsed.query, keep_blank_values=False)
        filtered_query = {
            k: v for k, v in query_dict.items()
            if k.lower() not in TRACKING_QUERY_PARAMS
        }
        clean_query = urlencode(filtered_query, doseq=True)

        return urlunparse((scheme, netloc, path, parsed.params, clean_query, ""))
    except Exception:
        return url


def parse_flexible_datetime(date_str: Any) -> Tuple[Optional[datetime], str]:
    """
    Parses date strings deterministically (ISO-8601, RFC-2822, YYYY-MM-DD, etc.)
    into a timezone-aware datetime.
    Returns (aware_datetime, timezone_str).
    """
    if not date_str:
        return None, "Africa/Nairobi"

    if isinstance(date_str, datetime):
        if timezone.is_aware(date_str):
            return date_str, str(date_str.tzinfo)
        return timezone.make_aware(date_str, timezone.get_current_timezone()), "Africa/Nairobi"

    date_str_clean = str(date_str).strip()
    if not date_str_clean:
        return None, "Africa/Nairobi"

    # 1. Try RFC 2822 / 822 (standard in RSS feeds, e.g. 'Tue, 15 Oct 2026 14:00:00 GMT')
    try:
        dt = parsedate_to_datetime(date_str_clean)
        if dt:
            if not timezone.is_aware(dt):
                dt = timezone.make_aware(dt, py_timezone.utc)
            return dt, "UTC"
    except Exception:
        pass

    # 2. Try ISO-8601 variations (e.g. 2026-10-15T12:00:00Z, 2026-10-15)
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str_clean, fmt)
            if timezone.is_aware(dt):
                return dt, str(dt.tzinfo)
            else:
                return timezone.make_aware(dt, timezone.get_current_timezone()), "Africa/Nairobi"
        except ValueError:
            continue

    return None, "Africa/Nairobi"


def compute_content_hash(
    title: str,
    organization: str,
    description: str,
    deadline_iso: Optional[str] = None,
    application_url: str = "",
) -> str:
    """
    Generates a deterministic SHA-256 hash of stable opportunity fields.
    Does NOT hash unstable metadata like timestamps, scraping IDs, or view counts.
    """
    norm_title = normalize_whitespace(title).lower()
    norm_org = normalize_whitespace(organization).lower()
    # Normalize description by stripping whitespace and html tags
    desc_clean = re.sub(r"<[^>]+>", " ", description or "")
    norm_desc = normalize_whitespace(desc_clean).lower()[:1000] # First 1000 chars of text content
    deadline_part = deadline_iso or ""
    app_url_part = normalize_url(application_url)

    raw_payload = f"{norm_title}||{norm_org}||{norm_desc}||{deadline_part}||{app_url_part}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def normalize_opportunity_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full deterministic normalization of raw extracted dict into MwohaOS schema.
    """
    title = normalize_whitespace(data.get("title", ""))
    organization = normalize_whitespace(data.get("organization", ""))
    raw_desc = data.get("description", "")
    description = sanitize_html(raw_desc)
    source_url = normalize_url(data.get("source_url", ""))
    app_url = normalize_url(data.get("application_url", "")) or source_url

    posted_dt, _ = parse_flexible_datetime(data.get("posted_date"))
    deadline_dt, dl_tz = parse_flexible_datetime(data.get("deadline"))

    deadline_iso = deadline_dt.isoformat() if deadline_dt else None
    content_hash = compute_content_hash(
        title=title,
        organization=organization,
        description=description,
        deadline_iso=deadline_iso,
        application_url=app_url,
    )

    return {
        "title": title,
        "organization": organization,
        "description": description,
        "opportunity_type": data.get("opportunity_type", "JOB"),
        "sector": data.get("sector", "GENERAL"),
        "location": normalize_whitespace(data.get("location", "")),
        "country": normalize_whitespace(data.get("country", "")),
        "remote": bool(data.get("remote", False)),
        "posted_date": posted_dt,
        "deadline": deadline_dt,
        "deadline_timezone": dl_tz,
        "source_url": source_url,
        "application_url": app_url,
        "eligibility_text": normalize_whitespace(data.get("eligibility_text", "")),
        "requirements": normalize_whitespace(data.get("requirements", "")),
        "preferred_skills": normalize_whitespace(data.get("preferred_skills", "")),
        "compensation": normalize_whitespace(data.get("compensation", "")),
        "raw_content": data.get("raw_content", "")[:20000], # Cap raw snapshot at 20KB
        "content_hash": content_hash,
    }
