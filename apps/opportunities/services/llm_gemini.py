"""
MwohaOS Google Gemini API Provider — Milestone 3 (Primary Hosted Provider)
Communicates directly with Google Gemini API via official HTTP REST endpoint.
Uses json_object response MIME type or clean parsing, with bounded retries and token metrics.
"""
import json
import logging
import re
import time
from typing import Dict, Any, Optional
import requests
from django.conf import settings
from .llm_base import LLMProvider, build_extraction_prompt
from .schema import validate_and_normalize_ai_schema

logger = logging.getLogger("mwohaos.gemini")


class GeminiProvider(LLMProvider):
    """
    Primary hosted LLM provider using Google Gemini API directly.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key or getattr(settings, "GEMINI_API_KEY", "")
        self.model = model or getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
        self.timeout = timeout or getattr(settings, "GEMINI_TIMEOUT_SECONDS", 120)
        self.max_retries = max_retries or getattr(settings, "GEMINI_MAX_RETRIES", 2)

    def get_provider_name(self) -> str:
        return "GEMINI"

    def get_model_name(self) -> str:
        return self.model

    def _call_gemini_api(self, prompt: str, enforce_json: bool = True) -> Dict[str, Any]:
        """
        Executes HTTP POST to Google Gemini generateContent API with bounded retries.
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
            }
        }
        if enforce_json:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        attempts = 0
        backoff = 1.0

        while attempts <= self.max_retries:
            attempts += 1
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise ValueError("Gemini returned empty candidates list.")

                    first_cand = candidates[0]
                    content_parts = first_cand.get("content", {}).get("parts", [])
                    if not content_parts:
                        raise ValueError("Gemini response missing content parts.")

                    raw_text = content_parts[0].get("text", "")
                    usage = data.get("usageMetadata", {})

                    return {
                        "text": raw_text,
                        "input_tokens": usage.get("promptTokenCount"),
                        "output_tokens": usage.get("candidatesTokenCount"),
                    }

                # Handle Rate Limit (429) or Server Errors (5xx)
                if response.status_code == 429 or response.status_code >= 500:
                    logger.warning(f"Gemini API returned status {response.status_code}. Attempt {attempts}/{self.max_retries + 1}")
                    if attempts <= self.max_retries:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    response.raise_for_status()

                # Handle 4xx Client Errors (e.g. 400 Bad Request, 403 Forbidden)
                response.raise_for_status()

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Gemini connection error: {e}. Attempt {attempts}/{self.max_retries + 1}")
                if attempts <= self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise

        raise RuntimeError(f"Gemini API call failed after {self.max_retries} retries.")

    def extract_opportunity(self, content: str) -> Dict[str, Any]:
        """
        Submits prompt to Gemini and validates returned JSON schema.
        """
        prompt = build_extraction_prompt(content)
        result = self._call_gemini_api(prompt, enforce_json=True)
        raw_text = result["text"].strip()

        # Clean potential markdown fences ```json ... ```
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```[a-zA-Z]*\n", "", raw_text)
            raw_text = re.sub(r"\n```$", "", raw_text)

        parsed_json = json.loads(raw_text.strip())
        normalized = validate_and_normalize_ai_schema(parsed_json)
        normalized["_token_metrics"] = {
            "input_tokens": result.get("input_tokens"),
            "output_tokens": result.get("output_tokens"),
        }
        return normalized

    def summarize_opportunity(self, content: str) -> str:
        prompt = f"Summarize this opportunity in 2 clear sentences:\n\n{content[:5000]}"
        result = self._call_gemini_api(prompt, enforce_json=False)
        return result["text"].strip()
