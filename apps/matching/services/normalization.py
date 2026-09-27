"""
MwohaOS Matching Normalization & Snapshot Utility — Milestone 4
Normalizes skills, education degrees, sectors, and computes snapshot hashes for stale detection.
"""
import hashlib
import json
import re
from typing import Dict, Any, List
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity


# Controlled dictionary of skill aliases and standard canonical forms
SKILL_ALIASES = {
    # Earth Observation & Geospatial
    "gee": "google earth engine",
    "earth engine": "google earth engine",
    "google earth engine": "google earth engine",
    "remote sensing": "remote sensing",
    "satellite remote sensing": "remote sensing",
    "earth observation": "earth observation",
    "satellite imagery": "earth observation",
    "satellite data": "earth observation",
    "gis": "gis",
    "geographic information systems": "gis",
    "geographic information system": "gis",
    "postgis": "postgis",
    "qgis": "qgis",
    "arcgis": "arcgis",
    "sar": "synthetic aperture radar",
    "synthetic aperture radar": "synthetic aperture radar",
    "sentinel": "sentinel satellite imagery",
    "landsat": "landsat satellite imagery",
    "spatial analysis": "spatial analysis",
    "geospatial analysis": "spatial analysis",

    # Programming & Tech
    "python": "python",
    "python programming": "python",
    "python development": "python",
    "r": "r programming",
    "r programming": "r programming",
    "sql": "sql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "django": "django",
    "docker": "docker",
    "containerization": "docker",
    "kubernetes": "kubernetes",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "deep learning": "deep learning",
    "computer vision": "computer vision",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "javascript": "javascript",
    "typescript": "typescript",
    "git": "git",
    "version control": "git",

    # Domain & Soft Skills
    "climate resilience": "climate science",
    "climate change": "climate science",
    "climate science": "climate science",
    "meteorology": "climate science",
    "hydrology": "hydrology",
    "flood modeling": "hydrology",
    "food security": "agriculture",
    "agricultural monitoring": "agriculture",
    "agriculture": "agriculture",
    "project management": "project management",
    "research methodology": "scientific research",
    "scientific research": "scientific research",
    "technical writing": "technical writing",
    "leadership": "leadership",
}

# Related skills mappings (allows RELATED match credit)
RELATED_SKILLS_MAP = {
    "google earth engine": ["remote sensing", "gis", "earth observation", "python"],
    "remote sensing": ["gis", "earth observation", "spatial analysis", "synthetic aperture radar"],
    "earth observation": ["remote sensing", "gis", "climate science", "agriculture"],
    "gis": ["spatial analysis", "remote sensing", "qgis", "arcgis", "postgis"],
    "postgis": ["postgresql", "sql", "gis", "spatial analysis"],
    "postgresql": ["postgis", "sql", "databases"],
    "machine learning": ["deep learning", "computer vision", "python", "data science"],
    "computer vision": ["machine learning", "deep learning", "remote sensing", "python"],
    "agriculture": ["earth observation", "remote sensing", "food security", "climate science"],
    "climate science": ["earth observation", "remote sensing", "hydrology", "environmental modeling"],
}


def normalize_skill(skill_name: str) -> str:
    """Normalizes a skill string to its canonical lowercased representation."""
    if not skill_name:
        return ""
    clean = re.sub(r"[^\w\s-]", "", skill_name.strip().lower())
    clean = re.sub(r"\s+", " ", clean)
    return SKILL_ALIASES.get(clean, clean)


def are_skills_related(skill_a: str, skill_b: str) -> bool:
    """Checks if two skills are canonically related."""
    norm_a = normalize_skill(skill_a)
    norm_b = normalize_skill(skill_b)
    if norm_a == norm_b:
        return True
    if norm_b in RELATED_SKILLS_MAP.get(norm_a, []):
        return True
    if norm_a in RELATED_SKILLS_MAP.get(norm_b, []):
        return True
    return False


def compute_profile_snapshot_hash(profile: Profile) -> str:
    """
    Computes a deterministic SHA-256 hash of all profile qualifications, skills,
    experiences, and preferences to detect stale matches when the profile updates.
    """
    skills = sorted([s.name.lower() for s in profile.skills.all()])
    experiences = sorted([f"{e.company}:{e.title}:{e.start_date}" for e in profile.experiences.all()])
    educations = sorted([f"{ed.institution}:{ed.degree}:{ed.field_of_study}" for ed in profile.educations.all()])
    projects = sorted([p.title.lower() for p in profile.projects.all()])

    prefs = getattr(profile, "preferences", None)
    pref_data = ""
    if prefs:
        pref_data = f"{prefs.target_opportunity_types}:{prefs.target_sectors}:{prefs.work_modes}:{prefs.target_countries}"

    payload = {
        "user_id": str(profile.user_id),
        "headline": profile.headline,
        "location": profile.location,
        "country": profile.country,
        "skills": skills,
        "experiences": experiences,
        "educations": educations,
        "projects": projects,
        "preferences": pref_data,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else "",
    }
    raw_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


def compute_opportunity_snapshot_hash(opportunity: Opportunity) -> str:
    """Computes a deterministic hash of the opportunity's core content."""
    payload = {
        "title": opportunity.title,
        "organization": opportunity.organization,
        "opportunity_type": opportunity.opportunity_type,
        "sector": opportunity.sector,
        "location": opportunity.location,
        "country": opportunity.country,
        "remote": opportunity.remote,
        "deadline": opportunity.deadline.isoformat() if opportunity.deadline else "",
        "content_hash": opportunity.content_hash,
    }
    raw_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


def compute_intelligence_snapshot_hash(intel) -> str:
    """Computes a hash of the structured intelligence record."""
    if not intel:
        return ""
    payload = {
        "status": intel.extraction_status,
        "version": intel.extraction_version,
        "summary": intel.summary,
        "required_requirements": intel.required_requirements,
        "preferred_requirements": intel.preferred_requirements,
        "eligibility": intel.eligibility,
        "required_skills": intel.required_skills,
    }
    raw_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
