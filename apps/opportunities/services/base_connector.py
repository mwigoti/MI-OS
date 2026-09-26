"""
MwohaOS Base Connector Interface & Connectors Registry — Milestone 2
Connectors fetch, parse, and normalize opportunity feeds into the standard MwohaOS schema.
"""
from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, List, Optional
from .http_client import HttpClient
from .normalization import normalize_opportunity_payload

logger = logging.getLogger("mwohaos.connectors")


class BaseOpportunityConnector(ABC):
    """
    Standard interface for all MwohaOS opportunity connectors.
    Every connector encapsulates:
      - fetch(): calls HTTP/API safely
      - parse(): converts raw responses into unnormalized dictionaries
      - normalize(): invokes deterministic normalizer
    """
    slug: str = "base"
    name: str = "Base Connector"
    default_type: str = "JOB"
    default_sector: str = "GENERAL"

    def __init__(self, source_obj=None, http_client: Optional[HttpClient] = None):
        self.source_obj = source_obj
        self.http_client = http_client or HttpClient()

    @abstractmethod
    def fetch(self) -> Any:
        """Fetch raw payload from external public endpoint."""
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw response payload into a list of candidate opportunity dicts."""
        pass

    def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Apply deterministic normalization."""
        # Set connector defaults if not provided in raw item
        if "opportunity_type" not in raw_item or not raw_item["opportunity_type"]:
            raw_item["opportunity_type"] = self.default_type
        if "sector" not in raw_item or not raw_item["sector"]:
            raw_item["sector"] = self.default_sector

        return normalize_opportunity_payload(raw_item)
