from decimal import Decimal

from django.core.management.base import BaseCommand

from admissions.models import Cutoff, CutoffMetric, Institute, Program
from admissions.services import csv_cutoff_rows


class Command(BaseCommand):
    help = "Load real cutoff data from admissions/data/cutoffs_2025.csv."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing institute, program, and cutoff data before import.",
        )

    def handle(self, *args, **options):
        rows = csv_cutoff_rows()
        if not rows:
            self.stdout.write(self.style.WARNING("No cutoff rows found to import."))
            return

        if options["reset"]:
            Cutoff.objects.all().delete()
            Program.objects.all().delete()
            Institute.objects.all().delete()

        imported_rows = 0
        imported_programs = 0
        for row in rows:
            institute, _ = Institute.objects.update_or_create(
                acronym=row["institute_acronym"],
                defaults={
                    "name": row["institute_name"],
                    "city": row["city"],
                    "state": row["state"],
                    "preference_score": int(row.get("preference_score") or 50),
                },
            )
            program, created = Program.objects.update_or_create(
                institute=institute,
                name=row["program_name"],
                branch_code=row["branch_code"],
                defaults={
                    "degree": row.get("degree") or "M.Tech",
                    "coap_rounds": row.get("coap_rounds", ""),
                    "is_active": (row.get("is_active") or "true").lower() == "true",
                },
            )
            imported_programs += int(created)

            closing_rank = row.get("closing_rank", "").strip()
            Cutoff.objects.update_or_create(
                program=program,
                category=row["category"],
                year=int(row["year"]),
                defaults={
                    "min_score": Decimal(str(row["min_score"])),
                    "max_score": Decimal(str(row["max_score"])),
                    "metric_type": row.get("metric_type") or CutoffMetric.SCORE,
                    "closing_rank": int(closing_rank) if closing_rank else None,
                },
            )
            imported_rows += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {imported_rows} cutoff rows across {imported_programs} new programs."
            )
        )
