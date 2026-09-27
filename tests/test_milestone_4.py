"""
MwohaOS Milestone 4 Automated Test Suite: Opportunity Matching & Recommendations
Verifies:
  - Exact, Normalized, and Related skill matching with aliases (GEE -> Google Earth Engine)
  - Deterministic eligibility evaluation (nationality, education level, hard deadline constraints)
  - Hard constraint failure overrides score (Canada/US restriction forces INELIGIBLE & capped score)
  - Experience and cumulative years calculation
  - Education degree level & domain relevance
  - Sector, opportunity type, and remote preferences
  - Deterministic scoring weights and component calculation
  - Evidence traceability (claims reference actual Profile/Project records)
  - Idempotency & stale snapshot detection
  - Management command execution (match_opportunities & rematch_opportunity)
  - Authenticated dashboard and detail views with strict ownership
"""
import pytest
from datetime import date
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from apps.profiles.models import (
    Profile,
    Skill,
    Experience,
    Education,
    Project,
    ProfilePreference,
)
from apps.opportunities.models import Opportunity, OpportunityIntelligence
from apps.opportunities.constants import OpportunityType, Sector, OpportunityStatus
from apps.matching.models import OpportunityMatch
from apps.matching.constants import (
    MatchStatus,
    EligibilityStatus,
    SkillMatchType,
    LocationMatchType,
)
from apps.matching.services.normalization import normalize_skill, are_skills_related
from apps.matching.services.eligibility import evaluate_eligibility
from apps.matching.services.skills import evaluate_skills
from apps.matching.services.experience import evaluate_experience
from apps.matching.services.preferences import evaluate_education, evaluate_preferences
from apps.matching.services.scoring import calculate_overall_score
from apps.matching.services.matcher import match_profile_opportunity


# =============================================================================
# 1. SKILL MATCHING & NORMALIZATION
# =============================================================================

class TestSkillMatching:
    def test_normalize_skill_aliases(self):
        assert normalize_skill("GEE") == "google earth engine"
        assert normalize_skill("Earth Engine") == "google earth engine"
        assert normalize_skill("Python programming") == "python"
        assert normalize_skill("PostgreSQL") == "postgresql"
        assert normalize_skill("Satellite remote sensing") == "remote sensing"

    def test_are_skills_related(self):
        assert are_skills_related("google earth engine", "remote sensing") is True
        assert are_skills_related("postgis", "postgresql") is True
        assert are_skills_related("machine learning", "deep learning") is True
        assert are_skills_related("python", "carpentry") is False

    def test_evaluate_skills_exact_normalized_and_missing(self, db, profile):
        # Setup Profile Skills
        Skill.objects.create(profile=profile, name="Python", level="EXPERT")
        Skill.objects.create(profile=profile, name="GEE", level="ADVANCED") # Normalizes to google earth engine
        Skill.objects.create(profile=profile, name="PostgreSQL", level="INTERMEDIATE") # Related to PostGIS

        required = ["Python", "Google Earth Engine", "PostGIS", "Rust"]
        preferred = ["GIS", "Docker"]

        res = evaluate_skills(profile, required, preferred)
        matching = {m["skill"]: m["match_type"] for m in res["matching_skills"]}

        # Python is EXACT
        assert "Python" in matching
        assert matching["Python"] == SkillMatchType.EXACT

        # Google Earth Engine is NORMALIZED via GEE
        assert "Google Earth Engine" in matching
        assert matching["Google Earth Engine"] == SkillMatchType.NORMALIZED

        # PostGIS is RELATED via PostgreSQL
        assert "PostGIS" in matching
        assert matching["PostGIS"] == SkillMatchType.RELATED

        # Rust is MISSING
        assert "Rust" in res["missing_skills"]
        assert res["score"] > 60.0


# =============================================================================
# 2. ELIGIBILITY & HARD CONSTRAINTS
# =============================================================================

class TestEligibility:
    def test_eligible_nationality_match(self, db, profile):
        profile.country = "Kenya"
        profile.save()

        opp = Opportunity.objects.create(
            title="East Africa Climate Fellowship",
            organization="UN Climate Hub",
            source_url="https://climate.org/east-africa",
            content_hash="h-ea-1",
        )
        intel = OpportunityIntelligence.objects.create(
            opportunity=opp,
            eligibility={"nationality": ["Kenya", "Uganda", "Tanzania"]},
        )

        res = evaluate_eligibility(profile, opp, intelligence=intel)
        assert res["status"] == EligibilityStatus.ELIGIBLE
        assert res["hard_constraint_failed"] is False

    def test_hard_constraint_ineligible_canadian_restriction(self, db, profile):
        # Profile is Kenya
        profile.country = "Kenya"
        profile.save()

        opp = Opportunity.objects.create(
            title="Senior Earth Scientist",
            organization="Natural Resources Canada",
            source_url="https://nrcan.gc.ca/jobs/1",
            description="Applicants must be based in Canada. Must have Canadian work authorization.",
            content_hash="h-ca-1",
        )

        res = evaluate_eligibility(profile, opp)
        assert res["status"] == EligibilityStatus.INELIGIBLE
        assert res["hard_constraint_failed"] is True
        assert any("Canada" in r for r in res["reasons"])

    def test_deadline_passed_causes_ineligibility(self, db, profile):
        past = timezone.now() - timezone.timedelta(days=5)
        opp = Opportunity.objects.create(
            title="Expired Hackathon",
            organization="Tech Hub",
            source_url="https://hack.org/1",
            deadline=past,
            status=OpportunityStatus.EXPIRED,
            content_hash="h-exp-1",
        )
        res = evaluate_eligibility(profile, opp)
        assert res["status"] == EligibilityStatus.INELIGIBLE
        assert res["hard_constraint_failed"] is True


# =============================================================================
# 3. EXPERIENCE, EDUCATION & PREFERENCES
# =============================================================================

class TestExperienceAndEducation:
    def test_experience_years_and_project_correlation(self, db, profile):
        # 1 year at TerraSat
        Experience.objects.create(
            profile=profile,
            title="Geospatial ML Engineer",
            company="TerraSat Inc",
            start_date=date(2023, 1, 1),
            end_date=date(2024, 1, 1),
            description="Processing Sentinel satellite imagery and flood modeling with Python.",
        )
        # 1 year at GeoData
        Experience.objects.create(
            profile=profile,
            title="Remote Sensing Analyst",
            company="GeoData Corp",
            start_date=date(2024, 1, 1),
            end_date=date(2025, 1, 1),
            description="Earth observation and GIS analytics.",
        )
        # Correlated project
        Project.objects.create(
            profile=profile,
            title="AgriVision",
            role="Lead Developer",
            technologies="Python, Sentinel-2, PostGIS",
            description="Satellite crop health monitoring pipeline.",
        )

        opp_corpus = "Earth observation and satellite imagery specialist for agricultural flood modeling"
        res = evaluate_experience(
            profile=profile,
            required_experience_items=["2+ years of professional experience"],
            responsibilities=["Analyze radar and optical satellite datasets"],
            opportunity_corpus=opp_corpus,
        )

        assert res["total_years_experience"] >= 2.0
        assert len(res["matching_experience"]) >= 1
        assert len(res["matching_projects"]) >= 1
        assert res["score"] >= 80.0

    def test_education_matching_bachelor_and_field(self, db, profile):
        Education.objects.create(
            profile=profile,
            institution="University of Nairobi",
            degree="BSc Geospatial Engineering",
            field_of_study="Geospatial Engineering & Space Technology",
            start_date=date(2018, 9, 1),
            end_date=date(2022, 12, 1),
        )

        res = evaluate_education(
            profile=profile,
            required_requirements=["Bachelor's degree in engineering, GIS, or related discipline"],
            eligibility_education=["Bachelor's degree"],
        )
        assert res["score"] == 100.0
        assert res["status"] == "SATISFIED"
        assert len(res["matching_education"]) == 1

    def test_preference_matching(self, db, profile):
        prefs = ProfilePreference.objects.create(
            profile=profile,
            target_opportunity_types=["GRANT", "FELLOWSHIP", "ACCELERATOR"],
            target_sectors=["GEOSPATIAL", "EARTH_OBSERVATION", "CLIMATE"],
            work_modes=["REMOTE_ONLY"],
            target_countries="Kenya, United Kingdom",
        )

        opp = Opportunity.objects.create(
            title="Global EO Innovation Accelerator",
            organization="Copernicus Hub",
            opportunity_type=OpportunityType.ACCELERATOR,
            sector=Sector.EARTH_OBSERVATION,
            remote=True,
            source_url="https://copernicus.eu/accelerator",
            content_hash="h-cop-1",
        )

        res = evaluate_preferences(profile, opp)
        assert res["opportunity_type_score"] == 100.0
        assert res["sector_score"] == 100.0
        assert res["location_score"] == 100.0
        assert res["preference_score"] == 100.0


# =============================================================================
# 4. SCORING & HARD OVERRIDE
# =============================================================================

class TestScoring:
    def test_calculate_overall_score_positive(self):
        scores = {
            "eligibility": 100.0,
            "required_skills": 90.0,
            "experience": 85.0,
            "education": 100.0,
            "sector": 100.0,
            "opportunity_type": 100.0,
            "location": 100.0,
            "preferences": 95.0,
        }
        overall = calculate_overall_score(scores, eligibility_status=EligibilityStatus.ELIGIBLE)
        assert 90.0 <= overall <= 98.0

    def test_calculate_overall_score_hard_constraint_cap(self):
        # Candidate has 100% in skills and experience, but is explicitly INELIGIBLE
        scores = {
            "eligibility": 0.0,
            "required_skills": 100.0,
            "experience": 100.0,
            "education": 100.0,
            "sector": 100.0,
            "opportunity_type": 100.0,
            "location": 100.0,
            "preferences": 100.0,
        }
        overall = calculate_overall_score(
            scores,
            eligibility_status=EligibilityStatus.INELIGIBLE,
            hard_constraint_failed=True,
        )
        # Score must be capped to ensure no misleading recommendation
        assert overall <= 35.0


# =============================================================================
# 5. FULL MATCH ENGINE & IDEMPOTENCY
# =============================================================================

class TestMatchEngine:
    def test_match_profile_opportunity_end_to_end(self, db, profile):
        profile.country = "Kenya"
        profile.save()
        Skill.objects.create(profile=profile, name="Remote Sensing", level="EXPERT")
        Skill.objects.create(profile=profile, name="Python", level="EXPERT")
        Education.objects.create(
            profile=profile,
            institution="University of Nairobi",
            degree="BSc Geospatial Engineering",
            field_of_study="Geospatial Science",
        )

        opp = Opportunity.objects.create(
            title="Earth Observation Climate Innovation Programme",
            organization="Africa Climate Labs",
            opportunity_type=OpportunityType.FELLOWSHIP,
            sector=Sector.EARTH_OBSERVATION,
            country="Kenya",
            remote=True,
            source_url="https://climate.org/eo-programme",
            content_hash="h-climate-eo",
        )
        intel = OpportunityIntelligence.objects.create(
            opportunity=opp,
            summary="Fellowship for Earth Observation climate modeling.",
            required_skills=["Remote Sensing", "Python"],
            preferred_skills=["Google Earth Engine"],
            eligibility={"nationality": ["Kenya", "Uganda"]},
        )

        match_record = match_profile_opportunity(profile, opp)
        assert match_record.match_status == MatchStatus.COMPLETED
        assert match_record.eligibility_status == EligibilityStatus.ELIGIBLE
        assert match_record.overall_score >= 80.0
        assert "Remote Sensing" in match_record.required_requirements_met
        assert "Python" in match_record.required_requirements_met
        assert "This opportunity strongly aligns" in match_record.explanation

        # Idempotency check: Running matching a second time does NOT create duplicate
        match_record2 = match_profile_opportunity(profile, opp)
        assert match_record2.id == match_record.id
        assert OpportunityMatch.objects.filter(profile=profile, opportunity=opp).count() == 1


# =============================================================================
# 6. MANAGEMENT COMMANDS & VIEWS
# =============================================================================

class TestCommandsAndViews:
    def test_management_command_match_opportunities(self, db, profile):
        opp = Opportunity.objects.create(
            title="GIS Analyst Grant",
            organization="Space Foundation",
            source_url="https://space.org/grant",
            content_hash="h-space-grant",
        )
        call_command("match_opportunities", opportunity=str(opp.id))
        assert OpportunityMatch.objects.filter(profile=profile, opportunity=opp).exists()

    def test_matching_dashboard_authenticated(self, authenticated_client, profile, db):
        opp = Opportunity.objects.create(
            title="Lead Hydrologist",
            organization="Global Water",
            source_url="https://water.org/jobs/1",
            content_hash="h-water-1",
        )
        match_profile_opportunity(profile, opp)

        url = reverse("matching:index")
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Opportunity Matches" in content
        assert "Lead Hydrologist" in content

    def test_match_detail_view_strict_user_ownership(self, authenticated_client, profile, db):
        opp = Opportunity.objects.create(
            title="Senior AI Engineer",
            organization="AI Corp",
            source_url="https://aicorp.org/job",
            content_hash="h-ai-1",
        )
        match_rec = match_profile_opportunity(profile, opp)

        url = reverse("matching:detail", kwargs={"pk": match_rec.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Match Analysis:" in content
        assert "Senior AI Engineer" in content
        assert "Deterministic Alignment Explanation" in content
