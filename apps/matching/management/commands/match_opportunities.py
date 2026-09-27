"""
MwohaOS Management Commands: match_opportunities & rematch_opportunity — Milestone 4
"""
from django.core.management.base import BaseCommand, CommandError
from apps.profiles.models import Profile
from apps.opportunities.models import Opportunity
from apps.matching.models import OpportunityMatch
from apps.matching.services.matcher import match_profile_opportunity


class Command(BaseCommand):
    help = "Evaluates alignment matches between user profiles and opportunities."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pending",
            action="store_true",
            help="Match active opportunities not yet analyzed.",
        )
        parser.add_argument(
            "--profile",
            type=str,
            help="Profile ID or Username to match against.",
        )
        parser.add_argument(
            "--opportunity",
            type=str,
            help="Opportunity UUID to evaluate.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Re-evaluate all opportunities.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Max opportunities to process in this run.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Bypass stale checks and force re-calculation.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run calculation without saving to database.",
        )

    def handle(self, *args, **options):
        is_pending = options.get("pending")
        profile_arg = options.get("profile")
        opp_uuid = options.get("opportunity")
        process_all = options.get("all")
        limit = options.get("limit")
        force = options.get("force")
        dry_run = options.get("dry_run")

        # Resolve Profile
        if profile_arg:
            try:
                profile = Profile.objects.get(id=profile_arg)
            except (Profile.DoesNotExist, ValueError):
                try:
                    profile = Profile.objects.get(user__username=profile_arg)
                except Profile.DoesNotExist:
                    raise CommandError(f"Profile '{profile_arg}' not found.")
        else:
            profile = Profile.objects.first()
            if not profile:
                raise CommandError("No Profile records found in database. Create a profile first.")

        # Single Opportunity Match
        if opp_uuid:
            try:
                opp = Opportunity.objects.get(id=opp_uuid)
            except Opportunity.DoesNotExist:
                raise CommandError(f"Opportunity with ID '{opp_uuid}' does not exist.")

            self.stdout.write(f"Evaluating match for {profile.user.username} ↔ {opp.title}...")
            if not dry_run:
                match_record = match_profile_opportunity(profile, opp, force_refresh=force)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Match Complete: Score {match_record.overall_score:.1f}% | "
                        f"Eligibility: {match_record.eligibility_status} | Status: {match_record.match_status}"
                    )
                )
            else:
                self.stdout.write(self.style.WARNING("Dry-run: Calculation completed, no records saved."))
            return

        # Pending or Batch Match
        if is_pending or process_all:
            if is_pending:
                matched_ids = OpportunityMatch.objects.filter(profile=profile).values_list("opportunity_id", flat=True)
                opps = Opportunity.objects.exclude(id__in=matched_ids).filter(status="ACTIVE")[:limit]
            else:
                opps = Opportunity.objects.all()[:limit]

            count = opps.count()
            self.stdout.write(f"Processing matches for {profile.user.username} across {count} opportunities...")
            processed = 0
            for opp in opps:
                if not dry_run:
                    m = match_profile_opportunity(profile, opp, force_refresh=force)
                    self.stdout.write(f"  -> {opp.title[:45]}: {m.overall_score:.0f}% ({m.eligibility_status})")
                else:
                    self.stdout.write(f"  [Dry-run] -> {opp.title[:45]}")
                processed += 1

            self.stdout.write(self.style.SUCCESS(f"Finished processing {processed} opportunity matches."))
            return

        self.stdout.write(
            self.style.WARNING("Please specify --pending, --opportunity <uuid>, or --all. See --help for usage.")
        )
