"""
MwohaOS Structured AI Extraction Schema & Validation — Milestone 3
Ensures that all AI model outputs conform strictly to the required schema before storage.
Protects against malformed JSON, prompt injection leaks, and hallucinations.
"""
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger("mwohaos.schema")

# Canonical expected schema keys and their types
CANONICAL_SCHEMA = {
    "summary": str,
    "organization_summary": str,
    "purpose": str,
    "who_should_apply": list,
    "responsibilities": list,
    "required_requirements": list,
    "preferred_requirements": list,
    "eligibility": (dict, list),
    "required_documents": list,
    "required_experience": list,
    "required_skills": list,
    "preferred_skills": list,
    "benefits": list,
    "compensation_details": str,
    "location_details": str,
    "remote_details": str,
    "application_process": list,
    "important_dates": list,
    "application_instructions": list,
}


def sanitize_string_list(items: Any) -> List[str]:
    """Ensures input is a clean list of non-empty strings."""
    if not isinstance(items, list):
        if isinstance(items, str) and items.strip():
            return [items.strip()]
        return []
    result = []
    for item in items:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())
        elif isinstance(item, dict) and "name" in item:
            result.append(str(item["name"]).strip())
    return result


def validate_and_normalize_ai_schema(raw_dict: Any) -> Dict[str, Any]:
    """
    Validates that raw_dict conforms to CANONICAL_SCHEMA, coerces types gracefully,
    and returns a clean, fully-populated dictionary.
    """
    if not isinstance(raw_dict, dict):
        raise ValueError(f"AI output must be a JSON object, got {type(raw_dict)}")

    clean: Dict[str, Any] = {}

    clean["summary"] = str(raw_dict.get("summary") or "").strip()
    clean["organization_summary"] = str(raw_dict.get("organization_summary") or "").strip()
    clean["purpose"] = str(raw_dict.get("purpose") or "").strip()
    clean["compensation_details"] = str(raw_dict.get("compensation_details") or "").strip()
    clean["location_details"] = str(raw_dict.get("location_details") or "").strip()
    clean["remote_details"] = str(raw_dict.get("remote_details") or "").strip()

    clean["who_should_apply"] = sanitize_string_list(raw_dict.get("who_should_apply"))
    clean["responsibilities"] = sanitize_string_list(raw_dict.get("responsibilities"))
    clean["required_requirements"] = sanitize_string_list(raw_dict.get("required_requirements"))
    clean["preferred_requirements"] = sanitize_string_list(raw_dict.get("preferred_requirements"))
    clean["required_experience"] = sanitize_string_list(raw_dict.get("required_experience"))
    clean["required_skills"] = sanitize_string_list(raw_dict.get("required_skills"))
    clean["preferred_skills"] = sanitize_string_list(raw_dict.get("preferred_skills"))
    clean["benefits"] = sanitize_string_list(raw_dict.get("benefits"))
    clean["application_process"] = sanitize_string_list(raw_dict.get("application_process"))
    clean["application_instructions"] = sanitize_string_list(raw_dict.get("application_instructions"))

    # Eligibility normalization
    eligibility_raw = raw_dict.get("eligibility", {})
    if isinstance(eligibility_raw, dict):
        clean["eligibility"] = {
            "nationality": sanitize_string_list(eligibility_raw.get("nationality")),
            "residency": sanitize_string_list(eligibility_raw.get("residency")),
            "age": sanitize_string_list(eligibility_raw.get("age")),
            "education": sanitize_string_list(eligibility_raw.get("education")),
            "experience": sanitize_string_list(eligibility_raw.get("experience")),
            "organization_type": sanitize_string_list(eligibility_raw.get("organization_type")),
            "business_stage": sanitize_string_list(eligibility_raw.get("business_stage")),
            "geography": sanitize_string_list(eligibility_raw.get("geography")),
            "sector": sanitize_string_list(eligibility_raw.get("sector")),
            "other": sanitize_string_list(eligibility_raw.get("other")),
        }
    elif isinstance(eligibility_raw, list):
        clean["eligibility"] = {
            "nationality": [],
            "residency": [],
            "age": [],
            "education": [],
            "experience": [],
            "organization_type": [],
            "business_stage": [],
            "geography": [],
            "sector": [],
            "other": sanitize_string_list(eligibility_raw),
        }
    else:
        clean["eligibility"] = {}

    # Required documents normalization
    docs_raw = raw_dict.get("required_documents", [])
    clean_docs = []
    if isinstance(docs_raw, list):
        for doc in docs_raw:
            if isinstance(doc, dict):
                clean_docs.append({
                    "name": str(doc.get("name", "")).strip(),
                    "required": bool(doc.get("required", True)),
                    "conditional": bool(doc.get("conditional", False)),
                    "evidence": str(doc.get("evidence", "")).strip() or None,
                })
            elif isinstance(doc, str) and doc.strip():
                clean_docs.append({
                    "name": doc.strip(),
                    "required": True,
                    "conditional": False,
                    "evidence": None,
                })
    clean["required_documents"] = [d for d in clean_docs if d["name"]]

    # Important dates normalization
    dates_raw = raw_dict.get("important_dates", [])
    clean_dates = []
    if isinstance(dates_raw, list):
        for dt_item in dates_raw:
            if isinstance(dt_item, dict):
                clean_dates.append({
                    "name": str(dt_item.get("name", "Event")).strip(),
                    "date": str(dt_item.get("date", "")).strip(),
                    "timezone": str(dt_item.get("timezone", "")).strip() or None,
                    "confidence": float(dt_item.get("confidence", 0.90)),
                    "evidence": str(dt_item.get("evidence", "")).strip() or None,
                })
    clean["important_dates"] = clean_dates

    return clean
