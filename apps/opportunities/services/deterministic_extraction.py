"""
MwohaOS Deterministic Extraction & Deadline Intelligence Service — Milestone 3
Extracts obvious eligibility, document checklists, skill keywords, and calculates
deadline urgency without using AI.
"""
from datetime import datetime, timezone as py_timezone
import re
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.utils import timezone
from apps.opportunities.constants import DeadlineStatus
from apps.opportunities.services.normalization import normalize_whitespace, parse_flexible_datetime

# Controlled document types to detect
DOCUMENT_PATTERNS = [
    ("CV", r"\b(cv|curriculum vitae)\b"),
    ("Resume", r"\b(resume|resumés?)\b"),
    ("Cover Letter", r"\b(cover letter|letter of motivation|motivation letter)\b"),
    ("Portfolio", r"\b(portfolio|work samples?)\b"),
    ("Transcript", r"\b(transcript|academic records?)\b"),
    ("Degree Certificate", r"\b(degree certificate|diploma|graduation certificate)\b"),
    ("Recommendation Letter", r"\b(recommendation letter|letters? of recommendation|referee reports?)\b"),
    ("Research Proposal", r"\b(research proposal|project proposal|concept note)\b"),
    ("Business Plan", r"\b(business plan|pitch deck|executive summary)\b"),
    ("Pitch Deck", r"\b(pitch deck|slide deck)\b"),
    ("Budget", r"\b(budget|financial plan|cost breakdown)\b"),
    ("Letter of Intent", r"\b(letter of intent|expression of interest)\b"),
    ("Proof of Registration", r"\b(proof of registration|certificate of incorporation)\b"),
]

# Obvious technical and domain skills keywords
COMMON_TECHNICAL_SKILLS = [
    "Python", "R", "SQL", "PostGIS", "GIS", "QGIS", "ArcGIS", "Google Earth Engine",
    "Remote Sensing", "SAR", "Sentinel", "Landsat", "Machine Learning", "Deep Learning",
    "Computer Vision", "Docker", "Kubernetes", "Django", "PostgreSQL", "JavaScript",
    "TypeScript", "React", "Linux", "Git", "C++", "Rust", "TensorFlow", "PyTorch",
]

COMMON_DOMAIN_SKILLS = [
    "Earth Observation", "Climate Science", "Hydrology", "Disaster Risk Reduction",
    "Agriculture", "Food Security", "Deforestation Monitoring", "Satellite Data",
    "Spatial Analysis", "Environmental Modeling", "Photogrammetry", "Geodesy",
]

COMMON_PROFESSIONAL_SKILLS = [
    "Project Management", "Leadership", "Technical Writing", "Public Speaking",
    "Scientific Communication", "Grant Writing", "Data Analysis", "Research Methodology",
]


class DeadlineIntelligence:
    """Calculates deadline countdown, urgency, and lifecycle status."""

    @staticmethod
    def evaluate(deadline: Optional[datetime], deadline_timezone: str = "Africa/Nairobi") -> Dict[str, Any]:
        closing_soon_days = getattr(settings, "OPPORTUNITY_CLOSING_SOON_DAYS", 7)
        if not deadline:
            return {
                "deadline": None,
                "deadline_timezone": deadline_timezone,
                "deadline_status": DeadlineStatus.NO_DEADLINE,
                "days_remaining": None,
                "deadline_confidence": 0.5,
            }

        now = timezone.now()
        diff = deadline - now
        days_remaining = diff.total_seconds() / 86400.0

        if days_remaining < 0:
            status = DeadlineStatus.CLOSED
        elif days_remaining <= closing_soon_days:
            status = DeadlineStatus.CLOSING_SOON
        else:
            status = DeadlineStatus.OPEN

        return {
            "deadline": deadline.isoformat() if hasattr(deadline, "isoformat") else str(deadline),
            "deadline_timezone": deadline_timezone,
            "deadline_status": status,
            "days_remaining": round(days_remaining, 1) if days_remaining is not None else None,
            "deadline_confidence": 0.95,
        }


def extract_deterministic_intelligence(
    title: str,
    organization: str,
    description: str,
    deadline: Optional[datetime] = None,
    deadline_timezone: str = "Africa/Nairobi",
    raw_content: str = "",
) -> Dict[str, Any]:
    """
    Deterministic extraction from opportunity text before calling any AI provider.
    Extracts documents, skills, dates, and obvious requirements.
    """
    corpus = f"{title}\n{organization}\n{description}\n{raw_content}"
    corpus_lower = corpus.lower()

    # 1. Documents extraction
    extracted_docs = []
    for doc_name, pattern in DOCUMENT_PATTERNS:
        match = re.search(pattern, corpus_lower)
        if match:
            # Check context around match for 'required' or 'optional'
            start = max(0, match.start() - 60)
            end = min(len(corpus_lower), match.end() + 60)
            context = corpus[start:end]
            is_optional = any(opt in context.lower() for opt in ["optional", "if any", "preferred", "not mandatory"])
            extracted_docs.append({
                "name": doc_name,
                "required": not is_optional,
                "conditional": is_optional,
                "evidence": normalize_whitespace(context),
            })

    # 2. Skills extraction
    found_tech_skills = [s for s in COMMON_TECHNICAL_SKILLS if re.search(r"\b" + re.escape(s) + r"\b", corpus, re.IGNORECASE)]
    found_domain_skills = [s for s in COMMON_DOMAIN_SKILLS if re.search(r"\b" + re.escape(s) + r"\b", corpus, re.IGNORECASE)]
    found_prof_skills = [s for s in COMMON_PROFESSIONAL_SKILLS if re.search(r"\b" + re.escape(s) + r"\b", corpus, re.IGNORECASE)]
    all_skills = list(dict.fromkeys(found_tech_skills + found_domain_skills + found_prof_skills))

    # 3. Requirements & Preferred separation via regex lists
    required_lines = []
    preferred_lines = []
    lines = [line.strip() for line in description.split("\n") if line.strip()]

    in_required_section = False
    in_preferred_section = False

    for line in lines:
        l_lower = line.lower()
        if any(h in l_lower for h in ["requirements:", "qualifications:", "mandatory:", "eligibility criteria:"]):
            in_required_section = True
            in_preferred_section = False
            continue
        elif any(h in l_lower for h in ["preferred qualifications:", "nice to have:", "desirable:", "bonus:"]):
            in_preferred_section = True
            in_required_section = False
            continue
        elif line.startswith("#") or line.endswith(":"):
            in_required_section = False
            in_preferred_section = False

        if line.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.")):
            clean_item = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
            if in_required_section:
                required_lines.append(clean_item)
            elif in_preferred_section:
                preferred_lines.append(clean_item)

    # 4. Deadline intelligence
    deadline_info = DeadlineIntelligence.evaluate(deadline, deadline_timezone)

    # 5. Important dates
    important_dates = []
    if deadline:
        important_dates.append({
            "name": "Application Deadline",
            "date": deadline_info["deadline"],
            "timezone": deadline_timezone,
            "confidence": 0.95,
            "evidence": "Recorded deadline in opportunity database.",
        })

    # 6. Structured Eligibility baseline
    eligibility = {
        "nationality": [],
        "residency": [],
        "age": [],
        "education": [],
        "experience": [],
        "organization_type": [],
        "business_stage": [],
        "geography": [],
        "sector": [],
        "other": [],
    }

    # Extract obvious degree requirement
    if re.search(r"\b(phd|doctorate)\b", corpus_lower):
        eligibility["education"].append("PhD / Doctorate degree")
    elif re.search(r"\b(master'?s|msc|ma)\b", corpus_lower):
        eligibility["education"].append("Master's degree")
    elif re.search(r"\b(bachelor'?s|bsc|ba|undergraduate)\b", corpus_lower):
        eligibility["education"].append("Bachelor's degree")

    # Extract years of experience
    exp_match = re.search(r"(\d+)\+?\s*years?(?:\s+of)?\s+(?:professional\s+)?experience", corpus_lower)
    if exp_match:
        eligibility["experience"].append(f"{exp_match.group(1)}+ years professional experience")

    return {
        "summary": f"{title} at {organization}",
        "organization_summary": organization,
        "purpose": title,
        "who_should_apply": [],
        "responsibilities": [],
        "required_requirements": required_lines,
        "preferred_requirements": preferred_lines,
        "eligibility": eligibility,
        "required_documents": extracted_docs,
        "required_experience": eligibility["experience"],
        "required_skills": all_skills,
        "preferred_skills": [],
        "benefits": [],
        "compensation_details": "",
        "location_details": "",
        "remote_details": "",
        "application_process": [],
        "important_dates": important_dates,
        "application_instructions": [],
        "deadline_info": deadline_info,
        "confidence": 0.70,
    }
