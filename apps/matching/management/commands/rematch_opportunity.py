"""
MwohaOS Management Command: rematch_opportunity — Milestone 4
"""
from django.core.management.base import BaseCommand, CommandError
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity
from apps.matching.services.matcher import match_profile_opportunity


class Command(BaseCommand):
    help = "Forces recalculation of a match for a specific opportunity across user profiles."

    def add_arguments(self, parser):
        parser.add_argument("opportunity_id", type=str, help="UUID of the opportunity to rematch.")
        parser.add_argument("--profile", type=str, help="Optional user profile username or ID.")

    def handle(self, *args, **options):
        opp_id = options.get("opportunity_id")
        profile_arg = options.get("profile")

        try:
            opp = Opportunity.objects.get(id=opp_id)
        except Opportunity.DoesNotExist:
            raise CommandError(f"Opportunity with ID '{opp_id}' not found.")

        if profile_arg:
            try:
                profile = Profile.objects.get(user__username=profile_arg)
            except Profile.DoesNotExist:
                profile = Profile.objects.get(id=profile_arg)
            profiles = [profile]
        else:
            profiles = list(Profile.objects.all())

        if not profiles:
            raise CommandError("No user profiles found.")

        for p in profiles:
            self.stdout.write(f"Recalculating match for {p.user.username} ↔ {opp.title}...")
            m = match_profile_opportunity(p, opp, force_refresh=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated: {m.overall_score:.1f}% [{m.eligibility_status}] - {m.score_band_label}"
                )
            )
