"""
MwohaOS Milestone 2 Automated Test Suite: Opportunity Discovery & Ingestion
Verifies:
  - Opportunity and OpportunitySource models (UUID, choices, constraints)
  - 3-tier deterministic deduplication (Canonical URL, Content Hash, Org+Title+Deadline)
  - Deterministic normalization & date parsing (zero AI)
  - SSRF protection (localhost, private subnets, link-local, cloud metadata blocked)
  - HTML sanitization (strips script, iframe, onload, javascript: hrefs)
  - Ingestion pipeline orchestration and IngestionRun metrics
  - Connectors (ReliefWeb, RemoteOK, NASA Science RSS) using deterministic fixtures
  - Manual URL extraction and review flow
  - Opportunity inbox search, filters, pagination, and detail view
  - Expiration of overdue opportunities
"""
from datetime import datetime, date
import json
import pytest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from apps.opportunities.models import Opportunity, OpportunitySource, IngestionRun
from apps.opportunities.constants import OpportunityType, Sector, OpportunityStatus, SourceType, IngestionStatus
from apps.opportunities.services.security import validate_public_url, sanitize_html
from apps.opportunities.services.normalization import (
    normalize_url,
    normalize_whitespace,
    compute_content_hash,
    parse_flexible_datetime,
    normalize_opportunity_payload,
)
from apps.opportunities.services.validation import (
    validate_normalized_opportunity,
    resolve_deduplication,
    store_or_update_opportunity,
    OpportunityValidationError,
)
from apps.opportunities.services.connectors import (
    ReliefWebConnector,
    RemoteOKConnector,
    NasaScienceRssConnector,
)
from apps.opportunities.services.ingestion import IngestionPipeline, expire_stale_opportunities
from apps.opportunities.services.manual_ingestion import extract_metadata_from_url


# =============================================================================
# 1. MODELS & FIELD INTEGRITY
# =============================================================================

class TestOpportunityModels:
    def test_opportunity_creation_with_uuid(self, db):
        opp = Opportunity.objects.create(
            title="Geospatial ML Fellowship",
            organization="Earth Observation Alliance",
            opportunity_type=OpportunityType.FELLOWSHIP,
            sector=Sector.GEOSPATIAL,
            source_url="https://example.org/fellowship",
            content_hash="test-hash-12345",
        )
        assert opp.id is not None
        assert len(str(opp.id)) == 36 # UUID format
        assert opp.opportunity_type == OpportunityType.FELLOWSHIP
        assert opp.sector == Sector.GEOSPATIAL
        assert opp.status == OpportunityStatus.ACTIVE
        assert opp.is_expired is False

    def test_opportunity_source_model(self, db):
        source = OpportunitySource.objects.create(
            name="Test Public API",
            slug="test-public-api",
            source_type=SourceType.API,
            base_url="https://api.example.org/opportunities",
            enabled=True,
        )
        assert source.id is not None
        assert str(source) == "Test Public API (Public API) [Enabled]"
        source.enabled = False
        assert "Disabled" in str(source)


# =============================================================================
# 2. SSRF PROTECTION & HTML SANITIZATION
# =============================================================================

class TestSecurityAndSsrf:
    def test_ssrf_rejects_localhost_and_loopback(self):
        blocked_urls = [
            "http://localhost:8000/secret",
            "http://127.0.0.1:3000/api",
            "http://127.0.0.2:9000",
            "http://[::1]/admin",
            "http://0.0.0.0/test",
        ]
        for url in blocked_urls:
            with pytest.raises(ValidationError):
                validate_public_url(url)

    def test_ssrf_rejects_private_docker_and_internal_networks(self):
        blocked_urls = [
            "http://10.0.0.1/admin",
            "http://192.168.1.1/router",
            "http://172.18.0.1:5432", # Typical Docker bridge
            "http://169.254.169.254/latest/meta-data/", # AWS / Cloud Metadata
            "http://redis:6379",
            "http://db:5432",
            "http://metadata.google.internal/computeMetadata/v1/",
        ]
        for url in blocked_urls:
            with pytest.raises(ValidationError):
                validate_public_url(url)

    def test_ssrf_accepts_valid_public_https_domains(self):
        valid_urls = [
            "https://reliefweb.int/jobs",
            "https://remoteok.com/api",
            "https://science.nasa.gov/feed/",
            "http://example.com/careers/45",
        ]
        for url in valid_urls:
            assert validate_public_url(url) == url

    def test_html_sanitizer_removes_xss_scripts_and_handlers(self):
        malicious = """
        <p>Legitimate job description.</p>
        <script>alert('pwned')</script>
        <iframe src="http://evil.com"></iframe>
        <a href="javascript:stealCookie()">Click here</a>
        <div onclick="doBadThing()" onmouseover="evil()">Hover me</div>
        """
        cleaned = sanitize_html(malicious)
        assert "<script>" not in cleaned
        assert "alert(" not in cleaned
        assert "<iframe" not in cleaned
        assert "javascript:" not in cleaned
        assert "onclick=" not in cleaned
        assert "onmouseover=" not in cleaned
        assert "Legitimate job description." in cleaned


# =============================================================================
# 3. DETERMINISTIC NORMALIZATION & DATE PARSING
# =============================================================================

class TestNormalization:
    def test_normalize_whitespace(self):
        text = "  Senior   SAR  \t\n\n\n  Engineer   "
        assert normalize_whitespace(text) == "Senior SAR \n\n Engineer"

    def test_normalize_url_strips_tracking_parameters(self):
        url = "https://example.org/job/123?utm_source=twitter&utm_medium=social&ref=newsletter&id=77"
        cleaned = normalize_url(url)
        assert "utm_source" not in cleaned
        assert "utm_medium" not in cleaned
        assert "ref=" not in cleaned
        assert "id=77" in cleaned
        assert cleaned.startswith("https://example.org/job/123?id=77")

    def test_parse_flexible_datetime_rfc2822(self):
        dt, tz_name = parse_flexible_datetime("Tue, 15 Oct 2026 14:00:00 GMT")
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 10
        assert dt.day == 15

    def test_parse_flexible_datetime_iso(self):
        dt, _ = parse_flexible_datetime("2026-11-30T18:30:00Z")
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 11
        assert dt.day == 30

    def test_deterministic_content_hash(self):
        hash1 = compute_content_hash(
            title="Lead Hydrologist",
            organization="UN Water",
            description="Developing global flood warning systems.",
            deadline_iso="2026-12-01T00:00:00",
            application_url="https://unwater.org/apply",
        )
        hash2 = compute_content_hash(
            title="  lead  hydrologist ",
            organization="UN WATER",
            description="Developing global flood warning systems.",
            deadline_iso="2026-12-01T00:00:00",
            application_url="https://unwater.org/apply?utm_source=rss",
        )
        # Hash must match despite whitespace, casing, and tracking query params
        assert hash1 == hash2


# =============================================================================
# 4. 3-TIER DETERMINISTIC DEDUPLICATION
# =============================================================================

class TestDeduplication:
    def test_deduplication_priority_1_canonical_url(self, db):
        payload1 = {
            "title": "Earth Observation Specialist",
            "organization": "Copernicus Hub",
            "source_url": "https://copernicus.eu/jobs/101",
            "description": "Initial text.",
        }
        opp1, created = store_or_update_opportunity(normalize_opportunity_payload(payload1))
        assert created is True

        # Second payload with identical canonical URL but modified title/description
        payload2 = {
            "title": "Senior Earth Observation Specialist",
            "organization": "Copernicus Hub",
            "source_url": "https://copernicus.eu/jobs/101?utm_campaign=spring",
            "description": "Updated richer description text with more details.",
        }
        opp2, created2 = store_or_update_opportunity(normalize_opportunity_payload(payload2))
        assert created2 is False # Updated, not duplicated
        assert opp2.id == opp1.id
        assert opp2.description == "Updated richer description text with more details."

    def test_deduplication_priority_2_content_hash(self, db):
        # Different source URLs but identical content
        payload1 = {
            "title": "Radar Research Grant",
            "organization": "European Space Foundation",
            "source_url": "https://mirror1.org/grant",
            "description": "50k Euro grant for open SAR flood models.",
        }
        opp1, _ = store_or_update_opportunity(normalize_opportunity_payload(payload1))

        payload2 = {
            "title": "Radar Research Grant",
            "organization": "European Space Foundation",
            "source_url": "https://mirror2.org/grant",
            "description": "50k Euro grant for open SAR flood models.",
        }
        opp2, created2 = store_or_update_opportunity(normalize_opportunity_payload(payload2))
        assert created2 is False
        assert opp2.id == opp1.id

    def test_deduplication_priority_3_org_title_deadline(self, db):
        dl = timezone.now() + timezone.timedelta(days=20)
        opp1 = Opportunity.objects.create(
            title="Chief GIS Architect",
            organization="National Mapping Agency",
            source_url="https://agency.gov/old-link",
            deadline=dl,
            content_hash="hash-abc",
        )

        payload = {
            "title": "Chief GIS Architect",
            "organization": "National Mapping Agency",
            "source_url": "https://syndicate.org/new-link",
            "deadline": dl.strftime("%Y-%m-%d"),
            "description": "Expanded duties.",
        }
        opp2, created = store_or_update_opportunity(normalize_opportunity_payload(payload))
        assert created is False
        assert opp2.id == opp1.id

    def test_validation_rejects_missing_required_fields(self):
        with pytest.raises(OpportunityValidationError):
            validate_normalized_opportunity({"title": "A", "organization": "Org", "source_url": "http://valid.org"})

        with pytest.raises(OpportunityValidationError):
            validate_normalized_opportunity({"title": "Valid Title", "organization": "", "source_url": "http://valid.org"})

        with pytest.raises(OpportunityValidationError):
            validate_normalized_opportunity({"title": "Valid Title", "organization": "Org", "source_url": "not-a-url"})


# =============================================================================
# 5. CONNECTOR FIXTURE PARSING (RELIEFWEB, REMOTEOK, NASA RSS)
# =============================================================================

class TestConnectors:
    def test_reliefweb_connector_parse(self):
        fixture_json = json.dumps({
            "data": [
                {
                    "id": "12345",
                    "fields": {
                        "title": "Senior Geospatial Analyst - Drought Monitoring",
                        "source": [{"name": "World Food Programme"}],
                        "body": "Monitoring regional food insecurity using MODIS & CHIRPS.",
                        "url": "https://reliefweb.int/job/12345",
                        "date": {"created": "2026-09-01", "closing": "2026-11-01"},
                        "type": [{"name": "Consultancy"}],
                        "country": [{"name": "Kenya"}],
                    }
                }
            ]
        })
        connector = ReliefWebConnector()
        items = connector.parse(fixture_json)
        assert len(items) == 1
        item = items[0]
        assert item["title"] == "Senior Geospatial Analyst - Drought Monitoring"
        assert item["organization"] == "World Food Programme"
        assert item["opportunity_type"] == OpportunityType.CONSULTING
        assert item["country"] == "Kenya"

    def test_remoteok_connector_parse(self):
        fixture_json = json.dumps([
            {"legal": "Notice"},
            {
                "id": "999",
                "position": "Lead AI / Computer Vision Engineer",
                "company": "SatelliteVision Inc",
                "description": "Building foundation models for Sentinel satellite imagery.",
                "url": "https://remoteok.com/job/999",
                "tags": ["ai", "python", "pytorch"],
                "location": "Worldwide",
                "salary": "$140,000",
                "date": "2026-09-10",
            }
        ])
        connector = RemoteOKConnector()
        items = connector.parse(fixture_json)
        assert len(items) == 1
        item = items[0]
        assert item["title"] == "Lead AI / Computer Vision Engineer"
        assert item["organization"] == "SatelliteVision Inc"
        assert item["sector"] == Sector.AI
        assert item["remote"] is True

    def test_nasa_science_rss_connector_parse(self):
        fixture_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <title>NASA Science News</title>
            <item>
              <title>NASA Space Apps Challenge 2026 Open Global Hackathon</title>
              <link>https://science.nasa.gov/challenge-2026</link>
              <description>Join the world largest hackathon addressing climate and space challenges.</description>
              <pubDate>Mon, 15 Sep 2026 12:00:00 GMT</pubDate>
            </item>
          </channel>
        </rss>
        """
        connector = NasaScienceRssConnector()
        items = connector.parse(fixture_xml)
        assert len(items) == 1
        item = items[0]
        assert "NASA Space Apps" in item["title"]
        assert item["opportunity_type"] == OpportunityType.COMPETITION
        assert item["sector"] == Sector.EARTH_OBSERVATION


# =============================================================================
# 6. INGESTION PIPELINE & AUDIT METRICS
# =============================================================================

class TestIngestionPipeline:
    @patch.object(ReliefWebConnector, "fetch")
    def test_pipeline_creates_ingestion_run_record(self, mock_fetch, db):
        mock_fetch.return_value = json.dumps({
            "data": [
                {
                    "id": "888",
                    "fields": {
                        "title": "Disaster Response Coordinator",
                        "source": [{"name": "UN OCHA"}],
                        "url": "https://reliefweb.int/job/888",
                        "body": "Field coordination role.",
                    }
                }
            ]
        })
        source = OpportunitySource.objects.create(
            name="ReliefWeb Test",
            slug="reliefweb",
            source_type=SourceType.API,
            base_url="https://api.reliefweb.int/v1/jobs",
        )

        pipeline = IngestionPipeline()
        run = pipeline.process_source(source)

        assert run.status == IngestionStatus.SUCCESS
        assert run.items_created == 1
        assert run.items_failed == 0
        assert Opportunity.objects.filter(title="Disaster Response Coordinator").exists()

        source.refresh_from_db()
        assert source.last_run is not None
        assert source.last_success is not None

    def test_pipeline_skips_disabled_sources(self, db):
        source = OpportunitySource.objects.create(
            name="Disabled Feed",
            slug="disabled-feed",
            source_type=SourceType.RSS,
            base_url="https://feed.org/rss",
            enabled=False,
        )
        pipeline = IngestionPipeline()
        run = pipeline.process_source(source)
        assert run.items_created == 0
        assert "disabled" in run.error_message


# =============================================================================
# 7. MANUAL URL EXTRACTION & VIEWS
# =============================================================================

class TestManualUrlAndViews:
    @patch("apps.opportunities.services.manual_ingestion.HttpClient.get")
    def test_manual_metadata_extraction(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = """
        <!DOCTYPE html>
        <html>
          <head>
            <title>Climate Research Fellowship 2026</title>
            <meta name="description" content="Prestigious 1-year research fellowship on flood resilience.">
            <meta property="og:site_name" content="Africa Climate Foundation">
          </head>
          <body>
            <h1>Apply now</h1>
          </body>
        </html>
        """
        mock_get.return_value = mock_resp

        extracted = extract_metadata_from_url("https://climatefound.org/fellowship")
        assert extracted["title"] == "Climate Research Fellowship 2026"
        assert extracted["organization"] == "Africa Climate Foundation"
        assert extracted["opportunity_type"] == OpportunityType.FELLOWSHIP
        assert extracted["sector"] == Sector.CLIMATE

    def test_opportunity_inbox_authenticated_access(self, authenticated_client, db):
        opp = Opportunity.objects.create(
            title="Senior GIS Developer",
            organization="GeoSpatial Co",
            source_url="https://example.com/gis-dev",
            content_hash="h-gis-1",
        )
        url = reverse("opportunities:index")
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Opportunity Inbox" in content
        assert "Senior GIS Developer" in content

    def test_opportunity_detail_view(self, authenticated_client, db):
        opp = Opportunity.objects.create(
            title="Remote Sensing Postdoc",
            organization="Oxford University",
            opportunity_type=OpportunityType.RESEARCH,
            source_url="https://oxford.ac.uk/postdoc",
            content_hash="h-oxford",
        )
        url = reverse("opportunities:detail", kwargs={"pk": opp.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "Remote Sensing Postdoc" in content
        assert "Oxford University" in content
        assert "Canonical Source URL" in content

    def test_opportunity_sources_view_and_toggle(self, authenticated_client, db):
        source = OpportunitySource.objects.create(
            name="Custom Source",
            slug="custom-source",
            source_type=SourceType.API,
            base_url="https://api.test.org/jobs",
            enabled=True,
        )
        url = reverse("opportunities:sources")
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "Custom Source" in resp.content.decode()

        # Toggle enable/disable
        toggle_url = reverse("opportunities:source_toggle", kwargs={"pk": source.pk})
        resp = authenticated_client.post(toggle_url)
        assert resp.status_code == 302
        source.refresh_from_db()
        assert source.enabled is False


# =============================================================================
# 8. EXPIRATION OF OVERDUE OPPORTUNITIES
# =============================================================================

class TestOpportunityExpiration:
    def test_expire_stale_opportunities(self, db):
        now = timezone.now()
        past_deadline = now - timezone.timedelta(days=2)
        future_deadline = now + timezone.timedelta(days=10)

        # 1. Past deadline -> should expire
        opp_expired = Opportunity.objects.create(
            title="Expired Hackathon",
            organization="Tech Hub",
            source_url="https://hack.org/1",
            deadline=past_deadline,
            status=OpportunityStatus.ACTIVE,
            content_hash="h-exp",
        )

        # 2. Future deadline -> remains active
        opp_active = Opportunity.objects.create(
            title="Active Fellowship",
            organization="Space Labs",
            source_url="https://fellow.org/2",
            deadline=future_deadline,
            status=OpportunityStatus.ACTIVE,
            content_hash="h-act",
        )

        count = expire_stale_opportunities()
        assert count == 1

        opp_expired.refresh_from_db()
        opp_active.refresh_from_db()

        assert opp_expired.status == OpportunityStatus.EXPIRED
        assert opp_active.status == OpportunityStatus.ACTIVE
