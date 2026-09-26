"""
MwohaOS Opportunities Services Package — Milestone 2
"""
from .base_connector import BaseOpportunityConnector
from .connectors import (
    ReliefWebConnector,
    RemoteOKConnector,
    NasaScienceRssConnector,
    CONNECTOR_REGISTRY,
    get_connector_for_source,
)
from .http_client import HttpClient
from .ingestion import IngestionPipeline, expire_stale_opportunities
from .manual_ingestion import extract_metadata_from_url
from .normalization import (
    normalize_opportunity_payload,
    normalize_url,
    normalize_whitespace,
    compute_content_hash,
    parse_flexible_datetime,
)
from .security import validate_public_url, sanitize_html
from .validation import (
    store_or_update_opportunity,
    resolve_deduplication,
    validate_normalized_opportunity,
    OpportunityValidationError,
)

__all__ = [
    "BaseOpportunityConnector",
    "ReliefWebConnector",
    "RemoteOKConnector",
    "NasaScienceRssConnector",
    "CONNECTOR_REGISTRY",
    "get_connector_for_source",
    "HttpClient",
    "IngestionPipeline",
    "expire_stale_opportunities",
    "extract_metadata_from_url",
    "normalize_opportunity_payload",
    "normalize_url",
    "normalize_whitespace",
    "compute_content_hash",
    "parse_flexible_datetime",
    "validate_public_url",
    "sanitize_html",
    "store_or_update_opportunity",
    "resolve_deduplication",
    "validate_normalized_opportunity",
    "OpportunityValidationError",
]
