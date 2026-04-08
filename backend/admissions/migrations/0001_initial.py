# Generated for the GATE advisor initial schema.

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ApplicantSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("gate_score", models.PositiveSmallIntegerField()),
                (
                    "branch",
                    models.CharField(
                        choices=[
                            ("CS", "Computer Science"),
                            ("ME", "Mechanical"),
                            ("EE", "Electrical"),
                            ("EC", "Electronics"),
                            ("CE", "Civil"),
                            ("CH", "Chemical"),
                            ("IN", "Instrumentation"),
                            ("BT", "Biotechnology"),
                            ("XE", "Engineering Sciences"),
                            ("PI", "Production"),
                        ],
                        max_length=8,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("GENERAL", "General"),
                            ("OBC", "OBC-NCL"),
                            ("SC", "SC"),
                            ("ST", "ST"),
                            ("EWS", "EWS"),
                            ("PWD", "PwD"),
                        ],
                        max_length=12,
                    ),
                ),
                ("rank", models.PositiveIntegerField(blank=True, null=True)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("is_paid", models.BooleanField(default=False)),
                ("results_snapshot", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Institute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("acronym", models.CharField(max_length=24, unique=True)),
                ("city", models.CharField(max_length=80)),
                ("state", models.CharField(max_length=80)),
                ("preference_score", models.PositiveSmallIntegerField(default=50)),
            ],
            options={"ordering": ["-preference_score", "name"]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("razorpay_order_id", models.CharField(max_length=120, unique=True)),
                ("razorpay_payment_id", models.CharField(blank=True, max_length=120)),
                ("razorpay_signature", models.CharField(blank=True, max_length=256)),
                ("amount_paise", models.PositiveIntegerField(default=1000)),
                (
                    "status",
                    models.CharField(
                        choices=[("created", "Created"), ("paid", "Paid"), ("failed", "Failed")],
                        default="created",
                        max_length=16,
                    ),
                ),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "applicant_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="admissions.applicantsession",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Program",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("degree", models.CharField(default="M.Tech", max_length=80)),
                (
                    "branch_code",
                    models.CharField(
                        choices=[
                            ("CS", "Computer Science"),
                            ("ME", "Mechanical"),
                            ("EE", "Electrical"),
                            ("EC", "Electronics"),
                            ("CE", "Civil"),
                            ("CH", "Chemical"),
                            ("IN", "Instrumentation"),
                            ("BT", "Biotechnology"),
                            ("XE", "Engineering Sciences"),
                            ("PI", "Production"),
                        ],
                        max_length=8,
                    ),
                ),
                ("coap_rounds", models.CharField(blank=True, max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "institute",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="programs",
                        to="admissions.institute",
                    ),
                ),
            ],
            options={
                "ordering": ["institute__name", "name"],
                "unique_together": {("institute", "name", "branch_code")},
            },
        ),
        migrations.CreateModel(
            name="Cutoff",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("GENERAL", "General"),
                            ("OBC", "OBC-NCL"),
                            ("SC", "SC"),
                            ("ST", "ST"),
                            ("EWS", "EWS"),
                            ("PWD", "PwD"),
                        ],
                        max_length=12,
                    ),
                ),
                ("year", models.PositiveSmallIntegerField()),
                ("min_score", models.PositiveSmallIntegerField()),
                ("max_score", models.PositiveSmallIntegerField()),
                ("closing_rank", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cutoffs",
                        to="admissions.program",
                    ),
                ),
            ],
            options={
                "ordering": ["-year", "-max_score"],
                "unique_together": {("program", "category", "year")},
            },
        ),
    ]
