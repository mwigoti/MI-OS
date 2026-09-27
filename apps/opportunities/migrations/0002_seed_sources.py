"""
MwohaOS Opportunities Migration 0002: Seed Standard Public Opportunity Connectors
Seeds ReliefWeb (UN OCHA), RemoteOK, and NASA Science RSS feeds.
"""
from django.db import migrations


def seed_default_sources(apps, schema_editor):
    OpportunitySource = apps.get_model("opportunities", "OpportunitySource")

    sources = [
        {
            "name": "ReliefWeb (UN OCHA) Global Opportunities",
            "slug": "reliefweb",
            "source_type": "API",
            "base_url": "https://api.reliefweb.int/v1/jobs?appname=mwohaos-opportunity-bot&limit=25&profile=full",
            "enabled": True,
            "configuration": {
                "description": "UN OCHA humanitarian, climate, disaster risk, geospatial, and fellowship opportunities.",
            },
        },
        {
            "name": "RemoteOK Tech & Engineering Opportunities",
            "slug": "remoteok",
            "source_type": "API",
            "base_url": "https://remoteok.com/api",
            "enabled": True,
            "configuration": {
                "description": "Global verified remote software engineering, AI, and technical opportunities.",
            },
        },
        {
            "name": "NASA Science, Research & Innovation Feed",
            "slug": "nasa-science",
            "source_type": "RSS",
            "base_url": "https://science.nasa.gov/feed/",
            "enabled": True,
            "configuration": {
                "description": "NASA Earth Science research solicitations, fellowships, and challenges.",
            },
        },
    ]

    for item in sources:
        OpportunitySource.objects.get_or_create(
            slug=item["slug"],
            defaults={
                "name": item["name"],
                "source_type": item["source_type"],
                "base_url": item["base_url"],
                "enabled": item["enabled"],
                "configuration": item["configuration"],
            }
        )


def remove_default_sources(apps, schema_editor):
    OpportunitySource = apps.get_model("opportunities", "OpportunitySource")
    OpportunitySource.objects.filter(slug__in=["reliefweb", "remoteok", "nasa-science"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("opportunities", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_default_sources, remove_default_sources),
    ]
