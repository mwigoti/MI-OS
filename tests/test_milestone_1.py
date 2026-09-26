"""
MwohaOS Milestone 1 — Automated Test Suite: Profiles, Documents & Evidence Bank.
Verifies models, ownership isolation, CRUD, document security, date validation, and completeness.
"""
import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from apps.profiles.models import (
    Profile,
    Skill,
    Experience,
    Education,
    Project,
    Achievement,
    Certification,
    Publication,
    Language,
    ProfilePreference,
    Evidence,
)
from apps.documents.models import Document
from apps.profiles.services.completeness import calculate_profile_completeness

User = get_user_model()


@pytest.fixture
def other_user():
    return User.objects.create_user(
        username="other_person",
        email="other@mwohaos.local",
        password="OtherSecurePassword123!",
    )


@pytest.fixture
def user_profile(test_user):
    profile, _ = Profile.objects.get_or_create(
        user=test_user,
        defaults={
            "headline": "Lead Geospatial Engineer",
            "location": "Nairobi, Kenya",
            "country": "Kenya",
            "city": "Nairobi",
            "work_authorization": "Kenyan Citizen",
        }
    )
    return profile


@pytest.fixture
def other_profile(other_user):
    profile, _ = Profile.objects.get_or_create(
        user=other_user,
        defaults={
            "headline": "Software Architect",
            "location": "London, UK",
        }
    )
    return profile


# =============================================================================
# 1. PROFILE TESTS
# =============================================================================

class TestProfile:
    def test_profile_creation_and_fields(self, user_profile, test_user):
        assert user_profile.user == test_user
        assert user_profile.headline == "Lead Geospatial Engineer"
        assert str(user_profile) == f"Profile of {test_user.username}"

    def test_profile_overview_view_authenticated(self, authenticated_client):
        url = reverse("profiles:overview")
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "Professional Profile" in resp.content.decode()

    def test_profile_overview_anonymous_redirects(self, client):
        url = reverse("profiles:overview")
        resp = client.get(url)
        assert resp.status_code == 302
        assert "/accounts/login/" in resp.url

    def test_profile_edit_view(self, authenticated_client, user_profile):
        url = reverse("profiles:edit")
        data = {
            "headline": "Principal Remote Sensing Researcher",
            "professional_summary": "10+ years specializing in radar and optical Earth observation.",
            "location": "Nairobi, Kenya",
            "country": "Kenya",
            "city": "Nairobi",
            "phone": "+254711223344",
            "remote_preference": "REMOTE_ONLY",
            "availability": "AVAILABLE",
            "work_authorization": "Kenyan Citizen",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        user_profile.refresh_from_db()
        assert user_profile.headline == "Principal Remote Sensing Researcher"
        assert user_profile.remote_preference == "REMOTE_ONLY"
        assert user_profile.versions.count() >= 1


# =============================================================================
# 2. SKILLS TESTS
# =============================================================================

class TestSkills:
    def test_skill_crud(self, authenticated_client, user_profile):
        # Create
        url = reverse("profiles:skill_create")
        data = {
            "name": "Google Earth Engine",
            "category": "GEOSPATIAL",
            "proficiency": "ADVANCED",
            "years_experience": "4.5",
            "description": "Satellite imagery processing for agricultural yield estimation.",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        skill = Skill.objects.get(profile=user_profile, name="Google Earth Engine")
        assert skill.proficiency == "ADVANCED"

        # Edit
        edit_url = reverse("profiles:skill_edit", kwargs={"pk": skill.pk})
        resp = authenticated_client.post(edit_url, {
            "name": "Google Earth Engine",
            "category": "GEOSPATIAL",
            "proficiency": "EXPERT",
            "years_experience": "5.0",
        })
        assert resp.status_code == 302
        skill.refresh_from_db()
        assert skill.proficiency == "EXPERT"

        # Delete
        delete_url = reverse("profiles:skill_delete", kwargs={"pk": skill.pk})
        resp = authenticated_client.post(delete_url)
        assert resp.status_code == 302
        assert not Skill.objects.filter(pk=skill.pk).exists()

    def test_skill_ownership_isolation(self, authenticated_client, other_profile):
        # User A attempts to edit User B's skill
        other_skill = Skill.objects.create(
            profile=other_profile,
            name="Confidential Skill",
            category="OTHER",
            proficiency="BEGINNER",
        )
        edit_url = reverse("profiles:skill_edit", kwargs={"pk": other_skill.pk})
        resp = authenticated_client.get(edit_url)
        assert resp.status_code == 404


# =============================================================================
# 3. EXPERIENCE TESTS & DATE VALIDATION
# =============================================================================

class TestExperience:
    def test_experience_date_validation(self, user_profile):
        exp = Experience(
            profile=user_profile,
            organization="Space Labs Inc.",
            position="Remote Sensing Engineer",
            start_date=date(2023, 6, 1),
            end_date=date(2022, 6, 1), # End date before start date
            is_current=False,
        )
        with pytest.raises(ValidationError):
            exp.clean()

    def test_current_experience_allows_blank_end_date(self, user_profile):
        exp = Experience(
            profile=user_profile,
            organization="Space Labs Inc.",
            position="Remote Sensing Engineer",
            start_date=date(2023, 1, 1),
            end_date=None,
            is_current=True,
        )
        exp.clean() # Should not raise
        exp.save()
        assert exp.is_current is True

    def test_experience_ownership_isolation(self, authenticated_client, other_profile):
        other_exp = Experience.objects.create(
            profile=other_profile,
            organization="Secret Agency",
            position="Analyst",
            start_date=date(2022, 1, 1),
        )
        edit_url = reverse("profiles:experience_edit", kwargs={"pk": other_exp.pk})
        resp = authenticated_client.get(edit_url)
        assert resp.status_code == 404


# =============================================================================
# 4. EDUCATION TESTS
# =============================================================================

class TestEducation:
    def test_education_crud_and_validation(self, authenticated_client, user_profile):
        edu = Education(
            profile=user_profile,
            institution="University of Nairobi",
            degree="Bachelor of Science",
            field_of_study="Geospatial Information Science",
            start_date=date(2018, 9, 1),
            end_date=date(2017, 9, 1),
        )
        with pytest.raises(ValidationError):
            edu.clean()

        edu.end_date = date(2022, 12, 1)
        edu.clean()
        edu.save()
        assert edu.pk is not None


# =============================================================================
# 5. PROJECTS & ACHIEVEMENTS TESTS
# =============================================================================

class TestProjectsAndAchievements:
    def test_project_crud(self, authenticated_client, user_profile):
        url = reverse("profiles:project_create")
        data = {
            "name": "Sentinel Flood Inundation Pipeline",
            "category": "EARTH_OBSERVATION",
            "role": "Lead Architect",
            "technologies": "Python, Sentinel-1, GDAL, PostGIS, Docker",
            "description": "Automated pipeline converting SAR GRD data to flood vulnerability maps.",
            "impact": "Deployed across 3 river basins, reducing manual disaster analysis latency by 85%.",
            "start_date": "2023-01-15",
            "is_current": True,
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        proj = Project.objects.get(profile=user_profile, name="Sentinel Flood Inundation Pipeline")
        assert proj.category == "EARTH_OBSERVATION"

    def test_achievement_crud(self, authenticated_client, user_profile):
        ach = Achievement.objects.create(
            profile=user_profile,
            title="Copernicus Masters Regional Winner",
            organization="European Space Agency",
            date=date(2024, 11, 1),
        )
        assert ach.pk is not None
        assert str(ach) == "Copernicus Masters Regional Winner (European Space Agency)"


# =============================================================================
# 6. CERTIFICATIONS & PUBLICATIONS TESTS
# =============================================================================

class TestCertificationsAndPublications:
    def test_certification_validation(self, user_profile):
        cert = Certification(
            profile=user_profile,
            name="AWS Certified Solutions Architect",
            issuer="Amazon Web Services",
            issue_date=date(2024, 5, 1),
            expiry_date=date(2023, 5, 1), # Expiry before issue date
        )
        with pytest.raises(ValidationError):
            cert.clean()

        cert.expiry_date = date(2027, 5, 1)
        cert.clean()
        cert.save()
        assert cert.pk is not None

    def test_publication_model(self, user_profile):
        pub = Publication.objects.create(
            profile=user_profile,
            title="High-Resolution SAR Analysis for Agricultural Flood Recovery",
            publication_type="JOURNAL",
            publisher="IEEE Geoscience & Remote Sensing Letters",
            authors="Mwoha, H., Smith, A.",
            publication_date=date(2024, 8, 1),
            doi="10.1109/LGRS.2024.123456",
        )
        assert str(pub) == "High-Resolution SAR Analysis for Agricultural Flood Recovery"


# =============================================================================
# 7. DOCUMENT MANAGEMENT & SECURITY TESTS
# =============================================================================

class TestDocumentSecurity:
    def test_document_upload_success(self, authenticated_client, user_profile):
        url = reverse("documents:upload")
        fake_file = SimpleUploadedFile("geospatial_cv.pdf", b"%PDF-1.4 Fake PDF Content", content_type="application/pdf")
        data = {
            "title": "Geospatial Specialized CV (2026)",
            "document_type": "CV",
            "file": fake_file,
            "version": "2026.1",
            "is_primary": True,
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        doc = Document.objects.get(profile=user_profile, title="Geospatial Specialized CV (2026)")
        assert doc.is_primary is True
        assert doc.file_extension == "PDF"

    def test_document_disallows_forbidden_extension(self, authenticated_client, user_profile):
        url = reverse("documents:upload")
        dangerous_file = SimpleUploadedFile("malware.exe", b"binarycontent", content_type="application/x-msdownload")
        data = {
            "title": "Suspicious Executable",
            "document_type": "OTHER",
            "file": dangerous_file,
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 200
        assert "Unsupported file format" in resp.content.decode()

    def test_unauthorized_user_cannot_download_document(self, authenticated_client, other_profile):
        # User B has uploaded a private document
        other_file = SimpleUploadedFile("secret_resume.pdf", b"%PDF-1.4 confidential", content_type="application/pdf")
        other_doc = Document.objects.create(
            profile=other_profile,
            title="Confidential CV",
            document_type="RESUME",
            file=other_file,
        )

        # User A tries to download User B's document
        download_url = reverse("documents:download", kwargs={"pk": other_doc.pk})
        resp = authenticated_client.get(download_url)
        # Must return 404 (or 403) and NOT deliver User B's file
        assert resp.status_code == 404


# =============================================================================
# 8. EVIDENCE BANK & CLAIM VERIFICATION TESTS
# =============================================================================

class TestEvidenceBank:
    def test_evidence_creation_and_relationships(self, user_profile):
        proj = Project.objects.create(
            profile=user_profile,
            name="Flood Watch Alert System",
            description="Real-time river stage monitoring system.",
        )
        doc_file = SimpleUploadedFile("award_cert.pdf", b"%PDF-1.4 Award", content_type="application/pdf")
        doc = Document.objects.create(
            profile=user_profile,
            title="NASA Space Apps Certificate",
            document_type="CERTIFICATE",
            file=doc_file,
        )

        evidence = Evidence.objects.create(
            profile=user_profile,
            evidence_type="PROJECT",
            title="GitHub: Flood Watch Live Pipeline",
            claim_summary="Architected real-time hydrological forecasting algorithm",
            source_url="https://github.com/mwoha/flood-watch",
            related_project=proj,
            document=doc,
            verified=False,
        )
        assert evidence.verified is False
        assert evidence.related_project == proj
        assert evidence.document == doc

    def test_evidence_ownership_isolation(self, authenticated_client, other_profile):
        other_ev = Evidence.objects.create(
            profile=other_profile,
            title="Classified Evidence",
            evidence_type="PROJECT",
        )
        edit_url = reverse("profiles:evidence_edit", kwargs={"pk": other_ev.pk})
        resp = authenticated_client.get(edit_url)
        assert resp.status_code == 404


# =============================================================================
# 9. DETERMINISTIC PROFILE COMPLETENESS TESTS
# =============================================================================

class TestProfileCompleteness:
    def test_empty_profile_completeness(self, test_user):
        empty_profile = Profile.objects.create(user=test_user)
        result = calculate_profile_completeness(empty_profile)
        assert result["overall"] < 20
        assert result["sections"]["experience"] == 0
        assert result["sections"]["skills"] == 0
        assert result["sections"]["projects"] == 0

    def test_completed_profile_deterministic_score(self, user_profile):
        user_profile.headline = "Senior Geospatial Systems Architect"
        user_profile.professional_summary = "Over a decade building high-throughput Earth observation pipelines and machine learning classifiers."
        user_profile.location = "Nairobi, Kenya"
        user_profile.linkedin_url = "https://linkedin.com/in/mwoha"
        user_profile.github_url = "https://github.com/mwoha"
        user_profile.save()

        # Add 2 experiences
        Experience.objects.create(profile=user_profile, organization="ESA", position="Fellow", start_date=date(2022, 1, 1), end_date=date(2023, 1, 1))
        Experience.objects.create(profile=user_profile, organization="RCMRD", position="Lead Specialist", start_date=date(2023, 2, 1), is_current=True)

        # Add 1 education
        Education.objects.create(profile=user_profile, institution="Jomo Kenyatta University", degree="BSc", field_of_study="Geomatics", start_date=date(2016, 9, 1))

        # Add 8 skills
        for i in range(8):
            Skill.objects.create(profile=user_profile, name=f"Skill-{i}")

        # Add 3 projects
        for i in range(3):
            Project.objects.create(profile=user_profile, name=f"Project-{i}", description=f"Details for project {i}")

        # Add 1 CV document
        f = SimpleUploadedFile("cv.pdf", b"%PDF", content_type="application/pdf")
        Document.objects.create(profile=user_profile, title="Main CV", document_type="CV", file=f)

        # Add 3 evidence items (1 verified)
        Evidence.objects.create(profile=user_profile, title="Proof 1", verified=True)
        Evidence.objects.create(profile=user_profile, title="Proof 2", verified=False)
        Evidence.objects.create(profile=user_profile, title="Proof 3", verified=False)

        # Preferences
        ProfilePreference.objects.create(
            profile=user_profile,
            target_opportunity_types=["Jobs", "Grants"],
            target_sectors=["Geospatial", "Climate"],
            work_modes=["Remote"],
        )

        res = calculate_profile_completeness(user_profile)
        assert res["overall"] >= 80
        assert res["sections"]["experience"] == 100
        assert res["sections"]["education"] == 100
        assert res["sections"]["skills"] == 100
        assert res["sections"]["projects"] == 100
        assert res["stats"]["verified_evidence_count"] == 1
