import uuid

from django.conf import settings
from django.db import models


class CutoffMetric(models.TextChoices):
    SCORE = "score", "Score"
    MARKS = "marks", "Marks"


class Category(models.TextChoices):
    GENERAL = "GENERAL", "General"
    GENERAL_PWD = "GENERAL_PWD", "General PwD"
    OBC_NCL = "OBC_NCL", "OBC-NCL"
    OBC_NCL_PWD = "OBC_NCL_PWD", "OBC-NCL PwD"
    SC = "SC", "SC"
    SC_PWD = "SC_PWD", "SC PwD"
    ST = "ST", "ST"
    ST_PWD = "ST_PWD", "ST PwD"
    EWS = "EWS", "EWS"
    EWS_PWD = "EWS_PWD", "EWS PwD"


class Branch(models.TextChoices):
    CS = "CS", "Computer Science"
    ME = "ME", "Mechanical"
    EE = "EE", "Electrical"
    EC = "EC", "Electronics"
    CE = "CE", "Civil"
    CH = "CH", "Chemical"
    IN = "IN", "Instrumentation"
    BT = "BT", "Biotechnology"
    XE = "XE", "Engineering Sciences"
    PI = "PI", "Production"


class Institute(models.Model):
    name = models.CharField(max_length=160)
    acronym = models.CharField(max_length=24, unique=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    preference_score = models.PositiveSmallIntegerField(default=50)

    class Meta:
        ordering = ["-preference_score", "name"]

    def __str__(self):
        return self.acronym


class Program(models.Model):
    institute = models.ForeignKey(Institute, related_name="programs", on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    degree = models.CharField(max_length=80, default="M.Tech")
    branch_code = models.CharField(max_length=8, choices=Branch.choices)
    coap_rounds = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["institute__name", "name"]
        unique_together = ("institute", "name", "branch_code")

    def __str__(self):
        return f"{self.institute.acronym} - {self.name}"


class Cutoff(models.Model):
    program = models.ForeignKey(Program, related_name="cutoffs", on_delete=models.CASCADE)
    category = models.CharField(max_length=12, choices=Category.choices)
    year = models.PositiveSmallIntegerField()
    min_score = models.DecimalField(max_digits=8, decimal_places=2)
    max_score = models.DecimalField(max_digits=8, decimal_places=2)
    metric_type = models.CharField(max_length=8, choices=CutoffMetric.choices, default=CutoffMetric.SCORE)
    closing_rank = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-year", "-max_score"]
        unique_together = ("program", "category", "year")

    def __str__(self):
        return f"{self.program} {self.category} {self.year}"


class ApplicantSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="applicant_sessions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    gate_score = models.PositiveSmallIntegerField()
    branch = models.CharField(max_length=8, choices=Branch.choices)
    category = models.CharField(max_length=12, choices=Category.choices)
    rank = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(blank=True)
    is_paid = models.BooleanField(default=False)
    results_snapshot = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.branch} {self.gate_score} {self.category}"


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    applicant_session = models.ForeignKey(
        ApplicantSession,
        related_name="payments",
        on_delete=models.CASCADE,
    )
    plan_code = models.CharField(max_length=24, default="weekly")
    razorpay_order_id = models.CharField(max_length=120, unique=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True)
    razorpay_signature = models.CharField(max_length=256, blank=True)
    amount_paise = models.PositiveIntegerField(default=1000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CREATED)
    subscription_started_at = models.DateTimeField(null=True, blank=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.razorpay_order_id} {self.status}"
