"""
MwohaOS Milestone 5 Automated Test Suite: Application Workspace
Verifies:
  - Application workspace initialization and idempotency (one application per profile+opportunity)
  - Auto-population of required documents from OpportunityIntelligence
  - Document vault auto-attachment for matching primary credentials
  - Application state machine transitions and audit activity logging
  - Questionnaire management, essay draft word/character limit validation
  - Deterministic submission readiness score calculation and blocker enforcement
  - User review signoff workflow and submission recording
  - Strict user profile data isolation (access control)
  - Management commands (update_application_readiness)
  - Authenticated view routing and dashboard metrics
"""
import pytest
from datetime import date, timedelta
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from apps.profiles.models import Profile, Skill, Experience
from apps.documents.models import Document
from apps.opportunities.models import Opportunity, OpportunityIntelligence
from apps.opportunities.constants import OpportunityType, Sector
from apps.matching.models import OpportunityMatch
from apps.matching.constants import MatchStatus, EligibilityStatus
from apps.applications.models import (
    Application,
    ApplicationDocument,
    ApplicationQuestion,
    ApplicationNote,
    ApplicationActivity,
)
from apps.applications.constants import (
    ApplicationStatus,
    ApplicationPriority,
    DocumentRole,
    DocumentAttachmentStatus,
    QuestionStatus,
    QuestionCategory,
    SubmissionMethod,
    ActivityType,
)
from apps.applications.services.readiness import evaluate_application_readiness
from apps.applications.services.pipeline import (
    create_or_get_application,
    transition_application_status,
    record_submission,
)


@pytest.fixture
def opp_with_intelligence(db):
    opp = Opportunity.objects.create(
        title="Senior Earth Observation Researcher",
        organization="European Space Agency",
        opportunity_type=OpportunityType.JOB,
        sector=Sector.EARTH_OBSERVATION,
        description="Senior EO research fellowship requiring Python, remote sensing, and PhD.",
        application_url="https://esa.int/apply/eo-99",
        deadline=timezone.localdate() + timedelta(days=20),
    )
    OpportunityIntelligence.objects.create(
        opportunity=opp,
        summary="ESA EO fellowship in Frascati, Italy.",
        required_requirements=["PhD in Remote Sensing", "Python expertise"],
        preferred_requirements=["PostGIS experience"],
        required_documents=["Curriculum Vitae", "Cover Letter / Statement of Intent", "Academic Transcripts"],
        extraction_status="COMPLETED",
        extraction_method="DETERMINISTIC",
    )
    return opp


@pytest.fixture
def user_vault_documents(db, user_profile):
    cv = Document.objects.create(
        profile=user_profile,
        title="2026 Academic CV",
        document_type=Document.DocumentType.CV,
        file="documents/user_test/cv.pdf",
        is_primary=True,
    )
    transcript = Document.objects.create(
        profile=user_profile,
        title="BSc University Transcript",
        document_type=Document.DocumentType.TRANSCRIPT,
        file="documents/user_test/transcript.pdf",
        is_primary=True,
    )
    return {"cv": cv, "transcript": transcript}


# =============================================================================
# 1. APPLICATION WORKSPACE INITIALIZATION & AUTO-POPULATION
# =============================================================================

@pytest.mark.django_db
class TestApplicationInitialization:
    def test_create_or_get_application_idempotency(self, user_profile, opp_with_intelligence):
        app1 = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        assert app1 is not None
        assert app1.status == ApplicationStatus.SAVED
        assert app1.portal_url == "https://esa.int/apply/eo-99"
        assert app1.target_submission_date == opp_with_intelligence.deadline

        # Second call returns identical application
        app2 = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        assert app1.id == app2.id
        assert Application.objects.filter(profile=user_profile, opportunity=opp_with_intelligence).count() == 1

    def test_auto_populate_documents_from_intelligence(self, user_profile, opp_with_intelligence, user_vault_documents):
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        docs = list(app.application_documents.all())
        
        # 3 documents required by intelligence: CV, Cover Letter, Academic Transcripts
        assert len(docs) == 3
        roles = [d.document_role for d in docs]
        assert DocumentRole.CV in roles
        assert DocumentRole.COVER_LETTER in roles
        assert DocumentRole.TRANSCRIPT in roles

        # Primary CV and Transcript from Vault should be automatically linked
        cv_slot = next(d for d in docs if d.document_role == DocumentRole.CV)
        assert cv_slot.document == user_vault_documents["cv"]
        assert cv_slot.status == DocumentAttachmentStatus.ATTACHED

        transcript_slot = next(d for d in docs if d.document_role == DocumentRole.TRANSCRIPT)
        assert transcript_slot.document == user_vault_documents["transcript"]
        assert transcript_slot.status == DocumentAttachmentStatus.ATTACHED

        # Cover Letter has no primary document in vault -> missing
        cl_slot = next(d for d in docs if d.document_role == DocumentRole.COVER_LETTER)
        assert cl_slot.document is None
        assert cl_slot.status == DocumentAttachmentStatus.MISSING

    def test_creation_logs_activity(self, user_profile, opp_with_intelligence):
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        activities = app.activities.all()
        assert activities.count() >= 1
        assert activities.first().activity_type == ActivityType.CREATED


# =============================================================================
# 2. APPLICATION LIFECYCLE & STATE TRANSITIONS
# =============================================================================

@pytest.mark.django_db
class TestApplicationLifecycle:
    def test_state_transitions(self, user_profile, opp_with_intelligence):
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        assert app.status == ApplicationStatus.SAVED

        transition_application_status(app, ApplicationStatus.PREPARING, notes="Started CV tailoring")
        app.refresh_from_db()
        assert app.status == ApplicationStatus.PREPARING

        transition_application_status(app, ApplicationStatus.READY_TO_SUBMIT)
        app.refresh_from_db()
        assert app.status == ApplicationStatus.READY_TO_SUBMIT

        # Transition to SUBMITTED sets submitted_at timestamp
        assert app.submitted_at is None
        transition_application_status(app, ApplicationStatus.SUBMITTED)
        app.refresh_from_db()
        assert app.status == ApplicationStatus.SUBMITTED
        assert app.submitted_at is not None

        # Verify activity logs
        status_activities = app.activities.filter(activity_type=ActivityType.STATUS_CHANGE)
        assert status_activities.count() == 3

    def test_record_submission(self, user_profile, opp_with_intelligence):
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        
        record_submission(
            application=app,
            submission_method=SubmissionMethod.PORTAL,
            confirmation_code="ESA-APP-2026-X9",
            submission_notes="Submitted via ESA Careers portal. Email confirmation received.",
        )
        app.refresh_from_db()

        assert app.status == ApplicationStatus.SUBMITTED
        assert app.submission_confirmation_code == "ESA-APP-2026-X9"
        assert app.submission_method == SubmissionMethod.PORTAL
        assert "ESA Careers portal" in app.submission_notes

        sub_activity = app.activities.filter(activity_type=ActivityType.SUBMISSION_RECORDED).first()
        assert sub_activity is not None
        assert "ESA-APP-2026-X9" in sub_activity.description


# =============================================================================
# 3. QUESTIONNAIRE DRAFTING & LIMIT VALIDATION
# =============================================================================

@pytest.mark.django_db
class TestApplicationQuestions:
    def test_word_count_and_char_count(self, user_profile, opp_with_intelligence):
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        q = ApplicationQuestion.objects.create(
            application=app,
            question_text="Why are you the ideal candidate for this Earth Observation role?",
            category=QuestionCategory.MOTIVATION,
            max_words=20,
            max_characters=150,
            answer_draft="I bring 5 years of remote sensing experience with deep knowledge of Sentinel and Landsat imagery.",
        )

        assert q.word_count == 15
        assert q.char_count == len(q.answer_draft)
        assert q.is_within_limits is True

        # Exceed word limit
        q.answer_draft = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twenty-one"
        assert q.word_count == 21
        assert q.is_within_limits is False


# =============================================================================
# 4. DETERMINISTIC READINESS EVALUATION
# =============================================================================

@pytest.mark.django_db
class TestApplicationReadiness:
    def test_readiness_scoring_and_blockers(self, user_profile, opp_with_intelligence, user_vault_documents):
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        
        # Initial state: Missing cover letter, no user signoff
        res1 = evaluate_application_readiness(app, save=True)
        assert res1["is_ready_to_submit"] is False
        assert len(res1["missing_documents"]) == 1
        assert "Cover Letter / Statement of Intent" in res1["missing_documents"][0]
        assert any("missing or unattached" in b for b in res1["blockers"])

        # Attach missing cover letter
        cl_doc = Document.objects.create(
            profile=user_profile,
            title="Customized Cover Letter",
            document_type=Document.DocumentType.COVER_LETTER,
            file="documents/user_test/cl.pdf",
        )
        cl_slot = app.application_documents.get(document_role=DocumentRole.COVER_LETTER)
        cl_slot.document = cl_doc
        cl_slot.status = DocumentAttachmentStatus.ATTACHED
        cl_slot.save()

        # Add mandatory question and answer it
        q = ApplicationQuestion.objects.create(
            application=app,
            question_text="Research Statement",
            is_required=True,
            max_words=100,
            answer_draft="My research proposal focuses on scalable crop yield forecasting using GEE.",
            status=QuestionStatus.FINAL,
        )

        res2 = evaluate_application_readiness(app, save=True)
        # All required docs attached, question answered!
        assert len(res2["missing_documents"]) == 0
        assert len(res2["unanswered_questions"]) == 0
        assert res2["is_ready_to_submit"] is True

        # Complete user signoff adds 20 review points
        app.user_review_completed = True
        app.user_reviewed_at = timezone.now()
        app.save()

        res3 = evaluate_application_readiness(app, save=True)
        assert res3["readiness_score"] >= 90
        assert res3["user_review_completed"] is True
        assert res3["is_ready_to_submit"] is True

    def test_overdue_deadline_triggers_blocker(self, user_profile, opp_with_intelligence):
        opp_with_intelligence.deadline = timezone.localdate() - timedelta(days=2)
        opp_with_intelligence.save()

        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        app.target_submission_date = opp_with_intelligence.deadline
        app.save()

        assert app.is_overdue is True
        res = evaluate_application_readiness(app, save=True)
        assert res["is_ready_to_submit"] is False
        assert any("passed" in b for b in res["blockers"])


# =============================================================================
# 5. USER ISOLATION & ACCESS CONTROL
# =============================================================================

@pytest.mark.django_db
class TestApplicationIsolation:
    def test_profile_isolation(self, client, user_profile, other_profile, opp_with_intelligence):
        # User 1 creates app
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)

        # Login as User 2 (other_profile.user)
        client.force_login(other_profile.user)

        # Accessing User 1's app detail must 404
        response = client.get(reverse("applications:detail", kwargs={"pk": app.pk}))
        assert response.status_code == 404

        # Posting status change to User 1's app must 404
        post_resp = client.post(reverse("applications:update_status", kwargs={"pk": app.pk}), {"status": "SUBMITTED"})
        assert post_resp.status_code == 404


# =============================================================================
# 6. MANAGEMENT COMMANDS & VIEWS
# =============================================================================

@pytest.mark.django_db
class TestManagementCommandAndViews:
    def test_update_application_readiness_command(self, user_profile, opp_with_intelligence):
        app = create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)
        app.readiness_score = 0
        app.save()

        call_command("update_application_readiness", "--all")
        app.refresh_from_db()
        assert app.readiness_score > 0

    def test_application_dashboard_view(self, client, test_user, user_profile, opp_with_intelligence):
        client.force_login(test_user)
        create_or_get_application(profile=user_profile, opportunity=opp_with_intelligence)

        response = client.get(reverse("applications:index"))
        assert response.status_code == 200
        assert "Senior Earth Observation Researcher" in response.content.decode()
        assert "Application Workspaces" in response.content.decode()
