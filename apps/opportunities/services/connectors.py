"""
MwohaOS Concrete Opportunity Connectors — Milestone 2
Implements 3 real, publicly accessible opportunity sources:
1. ReliefWeb Humanitarian & Climate Opportunities API / Feed (Jobs, Fellowships, Consultancies)
2. RemoteOK Tech & Software Public Feed (Remote Software, AI, Engineering)
3. NASA Earth Data / Open Geospatial Feed (Research, Fellowships, Hackathons & Space Science)
"""
import json
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from .base_connector import BaseOpportunityConnector
from apps.opportunities.constants import OpportunityType, Sector

logger = logging.getLogger("mwohaos.connectors")


class ReliefWebConnector(BaseOpportunityConnector):
    """
    ReliefWeb (UN OCHA) Public API & Opportunities Connector.
    Provides verified international humanitarian, climate, disaster risk, geospatial,
    consulting, and fellowship opportunities.
    Endpoint: https://api.reliefweb.int/v1/jobs?appname=mwohaos-opportunity-bot&limit=25&profile=full
    """
    slug = "reliefweb"
    name = "ReliefWeb (UN OCHA) Global Opportunities"
    default_type = OpportunityType.FELLOWSHIP
    default_sector = Sector.DISASTER_RISK

    def fetch(self) -> str:
        url = "https://api.reliefweb.int/v1/jobs?appname=mwohaos-opportunity-bot&limit=25&profile=full"
        if self.source_obj and self.source_obj.base_url:
            url = self.source_obj.base_url
        response = self.http_client.get(url)
        return response.text

    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        results = []
        if not raw_data:
            return results

        try:
            data = json.loads(raw_data)
        except Exception as e:
            logger.error(f"ReliefWeb JSON parse failure: {e}")
            return results

        items = data.get("data", [])
        for item in items:
            fields = item.get("fields", {})
            title = fields.get("title", "")
            if not title:
                continue

            # Organization extraction
            orgs = fields.get("source", [])
            org_name = orgs[0].get("name", "International Organization") if orgs else "United Nations / NGO"

            # Body / Description
            body = fields.get("body", "") or fields.get("body-html", "")

            # URL
            url = fields.get("url", "")
            if not url and item.get("id"):
                url = f"https://reliefweb.int/job/{item['id']}"

            # Dates
            date_dict = fields.get("date", {})
            posted_date = date_dict.get("created")
            closing_date = date_dict.get("closing")

            # Classification
            opp_type = OpportunityType.JOB
            type_list = fields.get("type", [])
            if type_list:
                t_name = type_list[0].get("name", "").lower()
                if "consultancy" in t_name or "consultant" in t_name:
                    opp_type = OpportunityType.CONSULTING
                elif "internship" in t_name:
                    opp_type = OpportunityType.INTERNSHIP
                elif "fellowship" in t_name:
                    opp_type = OpportunityType.FELLOWSHIP

            # Country
            countries = fields.get("country", [])
            country_name = countries[0].get("name", "") if countries else ""

            results.append({
                "title": title,
                "organization": org_name,
                "description": body,
                "opportunity_type": opp_type,
                "sector": Sector.DISASTER_RISK,
                "location": country_name,
                "country": country_name,
                "posted_date": posted_date,
                "deadline": closing_date,
                "source_url": url,
                "application_url": url,
                "raw_content": json.dumps(fields)[:5000],
            })

        return results


class RemoteOKConnector(BaseOpportunityConnector):
    """
    RemoteOK Public API Connector.
    Provides global verified remote software engineering, AI, and technical opportunities.
    Endpoint: https://remoteok.com/api
    """
    slug = "remoteok"
    name = "RemoteOK Tech & Engineering Opportunities"
    default_type = OpportunityType.JOB
    default_sector = Sector.SOFTWARE

    def fetch(self) -> str:
        url = "https://remoteok.com/api"
        if self.source_obj and self.source_obj.base_url:
            url = self.source_obj.base_url
        response = self.http_client.get(url)
        return response.text

    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        results = []
        if not raw_data:
            return results

        try:
            data = json.loads(raw_data)
        except Exception as e:
            logger.error(f"RemoteOK JSON parse failure: {e}")
            return results

        # RemoteOK returns a list; first element is legal notice
        if isinstance(data, list):
            items = data[1:] if len(data) > 1 and isinstance(data[0], dict) and "legal" in data[0] else data
        else:
            items = []

        for item in items:
            if not isinstance(item, dict):
                continue
            position = item.get("position", "")
            company = item.get("company", "")
            if not position or not company:
                continue

            desc = item.get("description", "")
            url = item.get("url", "") or f"https://remoteok.com/remote-jobs/{item.get('id', '')}"
            apply_url = item.get("apply_url", "") or url
            tags = item.get("tags", [])
            tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            compensation = item.get("salary", "") or ""

            # Check if tags suggest AI or Data
            sector = Sector.SOFTWARE
            tags_lower = [t.lower() for t in tags] if isinstance(tags, list) else []
            if any(t in tags_lower for t in ["ai", "machine learning", "ml", "nlp"]):
                sector = Sector.AI
            elif any(t in tags_lower for t in ["data", "data science", "analytics", "sql"]):
                sector = Sector.DATA

            results.append({
                "title": position,
                "organization": company,
                "description": desc,
                "opportunity_type": OpportunityType.JOB,
                "sector": sector,
                "location": item.get("location", "Remote"),
                "country": "Global",
                "remote": True,
                "posted_date": item.get("date"),
                "source_url": url,
                "application_url": apply_url,
                "preferred_skills": tags_str,
                "compensation": compensation,
                "raw_content": json.dumps(item)[:5000],
            })

        return results


class NasaScienceRssConnector(BaseOpportunityConnector):
    """
    NASA Science & Earth Data Public RSS Opportunities Connector.
    Provides research grants, science challenges, hackathons (NASA Space Apps), and fellowships.
    Endpoint: https://science.nasa.gov/feed/
    """
    slug = "nasa-science"
    name = "NASA Science, Research & Innovation Feed"
    default_type = OpportunityType.RESEARCH
    default_sector = Sector.EARTH_OBSERVATION

    def fetch(self) -> str:
        url = "https://science.nasa.gov/feed/"
        if self.source_obj and self.source_obj.base_url:
            url = self.source_obj.base_url
        response = self.http_client.get(url)
        return response.text

    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        results = []
        if not raw_data:
            return results

        try:
            root = ET.fromstring(raw_data)
        except Exception as e:
            logger.error(f"NASA RSS XML parse failure: {e}")
            return results

        # Find items under channel (standard RSS 2.0)
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else root.findall(".//item")

        for item in items:
            title_elem = item.find("title")
            link_elem = item.find("link")
            desc_elem = item.find("description")
            pub_date_elem = item.find("pubDate")

            title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
            pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ""

            if not title or not link:
                continue

            # Classify type based on title keywords
            t_lower = title.lower()
            opp_type = OpportunityType.RESEARCH
            if "grant" in t_lower or "funding" in t_lower or "solicitation" in t_lower:
                opp_type = OpportunityType.GRANT
            elif "fellowship" in t_lower or "postdoctoral" in t_lower:
                opp_type = OpportunityType.FELLOWSHIP
            elif "competition" in t_lower or "challenge" in t_lower or "hackathon" in t_lower:
                opp_type = OpportunityType.COMPETITION

            results.append({
                "title": title,
                "organization": "NASA (National Aeronautics and Space Administration)",
                "description": desc,
                "opportunity_type": opp_type,
                "sector": Sector.EARTH_OBSERVATION,
                "location": "Global / Remote",
                "country": "United States",
                "remote": True,
                "posted_date": pub_date,
                "source_url": link,
                "application_url": link,
                "raw_content": desc[:5000],
            })

        return results


CONNECTOR_REGISTRY = {
    "reliefweb": ReliefWebConnector,
    "remoteok": RemoteOKConnector,
    "nasa-science": NasaScienceRssConnector,
}


def get_connector_for_source(source_obj) -> BaseOpportunityConnector:
    """Instantiates the appropriate connector class for an OpportunitySource."""
    slug = source_obj.slug
    connector_cls = CONNECTOR_REGISTRY.get(slug)
    if not connector_cls:
        # Fallback to RSS connector if source_type == RSS
        if source_obj.source_type == "RSS":
            connector_cls = NasaScienceRssConnector
        else:
            connector_cls = ReliefWebConnector
    return connector_cls(source_obj=source_obj)
