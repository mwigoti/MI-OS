"""
MwohaOS LLM Provider Router & Usage Logger — Milestone 3
Orchestrates primary (Gemini), secondary (Hugging Face), and AI-disabled (None) strategies.
Automatically falls back on rate-limits, timeouts, and transient API failures while
auditing execution in AIUsageLog.
"""
import logging
from typing import Dict, Any, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from apps.opportunities.models import Opportunity, AIUsageLog
from apps.opportunities.constants import ExtractionProvider
from .llm_base import LLMProvider
from .llm_gemini import GeminiProvider
from .llm_huggingface import HuggingFaceProvider

logger = logging.getLogger("mwohaos.llm_router")


class LLMRouter:
    """
    Intelligent router directing requests through configured hosted providers.
    Order: Primary (default Gemini) -> Secondary Fallback (default HF) -> None.
    """

    def __init__(self):
        self.primary_name = getattr(settings, "LLM_PROVIDER", "gemini").lower()
        self.fallback_name = getattr(settings, "LLM_FALLBACK_PROVIDER", "huggingface").lower()
        self.enable_fallback = getattr(settings, "AI_ENABLE_FALLBACK", True)

        self.gemini_provider = GeminiProvider()
        self.hf_provider = HuggingFaceProvider()

    def get_provider_instance(self, name: str) -> Optional[LLMProvider]:
        if name == "gemini":
            return self.gemini_provider
        elif name in ("huggingface", "hf"):
            return self.hf_provider
        return None

    def extract_opportunity(
        self,
        content: str,
        opportunity: Optional[Opportunity] = None,
    ) -> Tuple[Optional[Dict[str, Any]], str, str]:
        """
        Attempts extraction through primary provider, falling back to secondary if configured.
        Returns: (extracted_data_or_None, provider_used, model_used)
        """
        if self.primary_name == "none":
            logger.info("AI extraction disabled via LLM_PROVIDER=none.")
            return None, ExtractionProvider.NONE, "none"

        primary = self.get_provider_instance(self.primary_name)
        fallback = self.get_provider_instance(self.fallback_name) if self.enable_fallback else None

        # 1. Try Primary Provider
        if primary:
            log_record = AIUsageLog.objects.create(
                provider=primary.get_provider_name(),
                model=primary.get_model_name(),
                opportunity=opportunity,
                requested_at=timezone.now(),
            )
            try:
                logger.info(f"Attempting extraction using primary provider: {primary.get_provider_name()}")
                data = primary.extract_opportunity(content)
                log_record.success = True
                log_record.completed_at = timezone.now()
                token_metrics = data.pop("_token_metrics", {})
                log_record.input_tokens = token_metrics.get("input_tokens")
                log_record.output_tokens = token_metrics.get("output_tokens")
                log_record.save()
                return data, primary.get_provider_name(), primary.get_model_name()
            except Exception as e:
                err_msg = str(e)
                log_record.success = False
                log_record.completed_at = timezone.now()
                log_record.error_type = type(e).__name__
                log_record.error_message = err_msg[:1000]
                log_record.save()
                logger.warning(f"Primary provider {primary.get_provider_name()} failed: {err_msg}")

        # 2. Try Fallback Provider if configured & primary failed
        if fallback and fallback != primary:
            fallback_log = AIUsageLog.objects.create(
                provider=fallback.get_provider_name(),
                model=fallback.get_model_name(),
                opportunity=opportunity,
                requested_at=timezone.now(),
            )
            try:
                logger.info(f"Falling back to secondary provider: {fallback.get_provider_name()}")
                data = fallback.extract_opportunity(content)
                fallback_log.success = True
                fallback_log.completed_at = timezone.now()
                token_metrics = data.pop("_token_metrics", {})
                fallback_log.input_tokens = token_metrics.get("input_tokens")
                fallback_log.output_tokens = token_metrics.get("output_tokens")
                fallback_log.save()
                return data, fallback.get_provider_name(), fallback.get_model_name()
            except Exception as fb_err:
                fb_msg = str(fb_err)
                fallback_log.success = False
                fallback_log.completed_at = timezone.now()
                fallback_log.error_type = type(fb_err).__name__
                fallback_log.error_message = fb_msg[:1000]
                fallback_log.save()
                logger.error(f"Fallback provider {fallback.get_provider_name()} also failed: {fb_msg}")

        # Both AI providers failed or disabled
        return None, ExtractionProvider.NONE, "none"
