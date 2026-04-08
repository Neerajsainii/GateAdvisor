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

        institute_cache = {}
        program_cache = {}

        if not options["reset"]:
            for institute in Institute.objects.all():
                institute_cache[institute.acronym] = institute
            for program in Program.objects.all():
                program_cache[(program.institute.acronym, program.name, program.branch_code)] = program

        imported_rows = 0
        imported_programs = 0

        for row in rows:
            acronym = row["institute_acronym"]
            institute = institute_cache.get(acronym)
            if institute is None:
                institute = Institute.objects.create(
                    acronym=acronym,
                    name=row["institute_name"],
                    city=row["city"],
                    state=row["state"],
                    preference_score=int(row.get("preference_score") or 50),
                )
                institute_cache[acronym] = institute
            elif not options["reset"]:
                institute.name = row["institute_name"]
                institute.city = row["city"]
                institute.state = row["state"]
                institute.preference_score = int(row.get("preference_score") or 50)
                institute.save()

            program_key = (acronym, row["program_name"], row["branch_code"])
            program = program_cache.get(program_key)
            if program is None:
                program = Program.objects.create(
                    institute=institute,
                    name=row["program_name"],
                    branch_code=row["branch_code"],
                    degree=row.get("degree") or "M.Tech",
                    coap_rounds=row.get("coap_rounds", ""),
                    is_active=(row.get("is_active") or "true").lower() == "true",
                )
                program_cache[program_key] = program
                imported_programs += 1
            elif not options["reset"]:
                program.degree = row.get("degree") or "M.Tech"
                program.coap_rounds = row.get("coap_rounds", "")
                program.is_active = (row.get("is_active") or "true").lower() == "true"
                program.save()

            closing_rank = row.get("closing_rank", "").strip()
            if options["reset"]:
                Cutoff.objects.create(
                    program=program,
                    category=row["category"],
                    year=int(row["year"]),
                    min_score=Decimal(str(row["min_score"])),
                    max_score=Decimal(str(row["max_score"])),
                    metric_type=row.get("metric_type") or CutoffMetric.SCORE,
                    closing_rank=int(closing_rank) if closing_rank else None,
                )
            else:
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
