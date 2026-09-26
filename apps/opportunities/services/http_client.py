"""
MwohaOS Reusable HTTP Client — Milestone 2
Provides robust, rate-limited, bounded-retry HTTP operations with User-Agent identification
and SSRF validation before connecting.
"""
import logging
import time
from typing import Optional, Dict, Any
import requests
from django.conf import settings
from .security import validate_public_url

logger = logging.getLogger("mwohaos.http")

DEFAULT_USER_AGENT = "MwohaOS-OpportunityBot/0.2.0 (+https://mwohaos.local/bot; personal opportunity crawler)"
DEFAULT_TIMEOUT = 15
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5


class HttpClient:
    """
    Polite HTTP Client with SSRF enforcement, bounded retries, and rate limiting.
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        user_agent: str = DEFAULT_USER_AGENT,
        validate_ssrf: bool = True,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.validate_ssrf = validate_ssrf
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """
        Executes an HTTP GET with SSRF protection, bounded retries, and exponential backoff.
        """
        if self.validate_ssrf:
            validate_public_url(url)

        req_headers = headers or {}
        attempts = 0

        while attempts < self.max_retries:
            attempts += 1
            try:
                response = self.session.get(
                    url,
                    headers=req_headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    **kwargs,
                )
                # Check for redirects that might lead to SSRF
                if self.validate_ssrf and response.history:
                    for resp in response.history:
                        validate_public_url(resp.url)
                    validate_public_url(response.url)

                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                # 4xx errors should not generally be retried (except 429)
                if response.status_code == 429 and attempts < self.max_retries:
                    retry_after = int(response.headers.get("Retry-After", 2))
                    time.sleep(retry_after)
                    continue
                if 400 <= response.status_code < 500:
                    logger.warning(f"HTTP {response.status_code} client error fetching {url}: {e}")
                    raise
                if attempts >= self.max_retries:
                    raise
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                logger.warning(f"Connection issue on attempt {attempts}/{self.max_retries} for {url}: {e}")
                if attempts >= self.max_retries:
                    raise
                time.sleep(DEFAULT_BACKOFF_FACTOR * (2 ** (attempts - 1)))

        raise requests.exceptions.RequestException(f"Failed to fetch {url} after {self.max_retries} attempts.")
