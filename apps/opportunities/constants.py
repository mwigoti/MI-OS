"""
MwohaOS Opportunities Constants — Milestone 2: Opportunity Discovery & Ingestion
Controlled vocabularies for cross-spectrum career, funding, fellowship, and academic opportunities.
"""
from django.db import models


class OpportunityType(models.TextChoices):
    """
    Controlled opportunity classifications.
    Supports career, funding, fellowship, competitions, and academic opportunities.
    """
    JOB = "JOB", "Job / Employment"
    INTERNSHIP = "INTERNSHIP", "Internship"
    FELLOWSHIP = "FELLOWSHIP", "Fellowship"
    GRANT = "GRANT", "Grant / Funding"
    SCHOLARSHIP = "SCHOLARSHIP", "Scholarship"
    COMPETITION = "COMPETITION", "Competition / Challenge"
    HACKATHON = "HACKATHON", "Hackathon"
    ACCELERATOR = "ACCELERATOR", "Accelerator"
    INCUBATOR = "INCUBATOR", "Incubator"
    RESEARCH = "RESEARCH", "Research Position"
    CONSULTING = "CONSULTING", "Consulting Engagement"
    FREELANCE = "FREELANCE", "Freelance Project"
    PROGRAM = "PROGRAM", "Training Program"
    BOOTCAMP = "BOOTCAMP", "Bootcamp"
    CONFERENCE = "CONFERENCE", "Conference / Symposium"
    OTHER = "OTHER", "Other Opportunity"


class Sector(models.TextChoices):
    """
    Domain sectors for opportunity categorization.
    """
    GEOSPATIAL = "GEOSPATIAL", "Geospatial & GIS"
    REMOTE_SENSING = "REMOTE_SENSING", "Remote Sensing & Satellite Tech"
    EARTH_OBSERVATION = "EARTH_OBSERVATION", "Earth Observation"
    SPACE = "SPACE", "Space Systems"
    CLIMATE = "CLIMATE", "Climate & Meteorology"
    AGRICULTURE = "AGRICULTURE", "Agriculture & Food Security"
    SOFTWARE = "SOFTWARE", "Software Engineering"
    AI = "AI", "Artificial Intelligence & ML"
    DATA = "DATA", "Data Science & Big Data"
    RESEARCH = "RESEARCH", "Scientific Research"
    ENGINEERING = "ENGINEERING", "General Engineering"
    ENTREPRENEURSHIP = "ENTREPRENEURSHIP", "Entrepreneurship & Startups"
    ENVIRONMENT = "ENVIRONMENT", "Environment & Ecology"
    DISASTER_RISK = "DISASTER_RISK", "Disaster Risk & Emergency"
    FINANCE = "FINANCE", "Finance & Economics"
    HEALTH = "HEALTH", "Public Health & Biotech"
    EDUCATION = "EDUCATION", "Education & Academics"
    GENERAL = "GENERAL", "General / Interdisciplinary"
    OTHER = "OTHER", "Other Sector"


class OpportunityStatus(models.TextChoices):
    """
    Lifecycle status of an opportunity in MwohaOS.
    """
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    CLOSED = "CLOSED", "Closed / Filled"
    ARCHIVED = "ARCHIVED", "Archived"


class SourceType(models.TextChoices):
    """
    Connector transport / protocol types.
    """
    RSS = "RSS", "RSS / Atom Feed"
    API = "API", "Public API"
    WEBSITE = "WEBSITE", "Structured Public Website"
    CAREER_PAGE = "CAREER_PAGE", "Organization Career Page"
    JOB_BOARD = "JOB_BOARD", "Public Job Board"
    MANUAL = "MANUAL", "Manual Submission"
    OTHER = "OTHER", "Other Connector"


class IngestionStatus(models.TextChoices):
    """
    Run result states for observability.
    """
    RUNNING = "RUNNING", "Running"
    SUCCESS = "SUCCESS", "Success"
    PARTIAL = "PARTIAL", "Partial Success"
    FAILED = "FAILED", "Failed"
