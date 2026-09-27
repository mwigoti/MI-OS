"""
MwohaOS Hugging Face Inference Provider — Milestone 3 (Secondary Hosted Fallback)
Uses Hugging Face Hosted Inference API / Router (chat completions compatible endpoint).
Never assumes unlimited compute; acts strictly as a resilient fallback.
"""
import json
import logging
import re
import time
from typing import Dict, Any, Optional
import requests
from django.conf import settings
from .llm_base import LLMProvider, build_extraction_prompt, EXTRACTION_SYSTEM_PROMPT
from .schema import validate_and_normalize_ai_schema

logger = logging.getLogger("mwohaos.huggingface")


class HuggingFaceProvider(LLMProvider):
    """
    Secondary fallback hosted LLM provider using Hugging Face Inference Providers.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key or getattr(settings, "HUGGINGFACE_API_KEY", "")
        self.model = model or getattr(settings, "HUGGINGFACE_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self.provider = provider or getattr(settings, "HUGGINGFACE_PROVIDER", "together")
        self.timeout = timeout or getattr(settings, "HUGGINGFACE_TIMEOUT_SECONDS", 120)
        self.max_retries = max_retries or getattr(settings, "HUGGINGFACE_MAX_RETRIES", 1)

    def get_provider_name(self) -> str:
        return "HUGGINGFACE"

    def get_model_name(self) -> str:
        return self.model

    def _call_hf_api(self, prompt: str) -> Dict[str, Any]:
        """
        Calls Hugging Face router chat completions endpoint.
        """
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY is not configured.")

        # Standard Hugging Face serverless / router endpoint
        endpoint = "https://api-inference.huggingface.co/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"BEGIN OPPORTUNITY CONTENT\n{prompt}\nEND OPPORTUNITY CONTENT"},
            ],
            "temperature": 0.1,
            "max_tokens": 2048,
        }

        attempts = 0
        backoff = 1.0

        while attempts <= self.max_retries:
            attempts += 1
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise ValueError("Hugging Face returned empty choices.")

                    text = choices[0].get("message", {}).get("content", "")
                    usage = data.get("usage", {})
                    return {
                        "text": text,
                        "input_tokens": usage.get("prompt_tokens"),
                        "output_tokens": usage.get("completion_tokens"),
                    }

                if response.status_code in (429, 503, 504) and attempts <= self.max_retries:
                    logger.warning(f"Hugging Face status {response.status_code}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                response.raise_for_status()

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Hugging Face network error: {e}. Attempt {attempts}")
                if attempts <= self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise

        raise RuntimeError(f"Hugging Face API call failed after {self.max_retries} attempts.")

    def extract_opportunity(self, content: str) -> Dict[str, Any]:
        """
        Extracts structured JSON via HF router.
        """
        result = self._call_hf_api(content)
        raw_text = result["text"].strip()

        # Find first '{' and last '}'
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1:
            raw_text = raw_text[start : end + 1]

        parsed_json = json.loads(raw_text)
        normalized = validate_and_normalize_ai_schema(parsed_json)
        normalized["_token_metrics"] = {
            "input_tokens": result.get("input_tokens"),
            "output_tokens": result.get("output_tokens"),
        }
        return normalized

    def summarize_opportunity(self, content: str) -> str:
        prompt = f"Summarize this opportunity in 2 sentences:\n{content[:4000]}"
        result = self._call_hf_api(prompt)
        return result["text"].strip()
