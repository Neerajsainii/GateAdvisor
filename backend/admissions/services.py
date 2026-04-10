import csv
import hashlib
import hmac
import uuid
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import razorpay
from django.conf import settings
from django.utils import timezone

from .models import ApplicantSession, Category, Cutoff, CutoffMetric, Institute, Payment, Program


DATA_DIR = Path(__file__).resolve().parent / "data"
REAL_CUTOFFS_CSV = DATA_DIR / "cutoffs_2025.csv"

PROBABILITY_WEIGHT = {"High": 3, "Medium": 2, "Low": 1, "Reach": 0, "Marks-based": 0}
MATCH_TYPE_WEIGHT = {"Direct": 40, "Allied": 20, "Interdisciplinary": 0}
ALL_BRANCHES = {"CS", "ME", "EE", "EC", "CE", "CH", "IN", "BT", "XE", "PI"}
ALLIED_BRANCH_MAP = {
    "CS": {"EC", "EE", "IN"},
    "EE": {"EC", "IN"},
    "EC": {"EE", "IN", "CS"},
    "IN": {"EE", "EC"},
    "ME": {"PI", "XE"},
    "PI": {"ME", "XE"},
    "XE": {"ME", "PI", "CH", "BT"},
    "CH": {"BT", "XE", "ME"},
    "BT": {"CH", "XE"},
    "CE": {"XE"},
}
PROGRAM_ELIGIBILITY_RULES = {
    "Communication and Signal Processing": {"EC", "IN", "CS"},
    "Communication Network and Signal Processing": {"EC", "IN", "CS"},
    "VLSI Design and Nanoelectronics": {"EC", "EE", "IN", "CS"},
    "VLSI Design": {"EC", "EE", "IN", "CS"},
    "Microelectronics and VLSI": {"EC", "EE", "IN", "CS"},
    "Microelectronics": {"EC", "EE", "IN", "CS"},
    "System-on-Chip Design": {"EC", "EE", "IN", "CS"},
    "Power Systems and Power Electronics": {"EE", "IN", "EC"},
    "Power Electronics & Power Systems": {"EE", "IN", "EC"},
    "Power Electronics and Power Systems": {"EE", "IN", "EC"},
    "Power Systems Engineering": {"EE", "IN", "EC"},
    "Advanced Manufacturing": {"ME", "PI"},
    "Manufacturing and Materials Engineering": {"ME", "PI", "XE"},
    "Manufacturing": {"ME", "PI"},
    "Mechanical Systems Design": {"ME"},
    "Mechanical System Design": {"ME"},
    "Thermal Energy Systems": {"ME"},
    "Thermal & Energy Systems Engineering": {"ME"},
    "Thermofluids Engineering": {"ME"},
    "Materials Science": {"ME", "CH", "EC", "EE", "XE"},
    "Materials Engineering": {"ME", "CH", "EC", "EE", "XE"},
    "Materials Science and Engineering": {"ME", "CH", "EC", "EE", "XE"},
    "Materials Science and Metallurgical Engineering": {"ME", "CH", "EC", "EE", "XE"},
    "Metallurgical Engineering": {"ME", "PI", "XE"},
    "Extractive Metallurgy": {"ME", "PI", "XE"},
    "Alloy Technology": {"ME", "PI", "XE"},
    "Space Engineering": {"EC", "EE", "IN", "CS", "XE"},
    "Applied Optics and Laser Technology": {"EC", "EE", "IN", "ME", "PI"},
    "Electric Vehicle Technology": {"ME", "EE", "EC", "PI", "IN", "XE"},
    "Biomedical Engineering": ALL_BRANCHES,
    "Biomedical Devices": {"CS", "EE", "EC", "IN", "ME", "BT", "XE"},
    "Medical Devices": ALL_BRANCHES,
    "Structural Engineering": {"CE"},
    "Transportation Systems Engineering": {"CE"},
    "Transportation Engineering": {"CE"},
    "Geotechnical Engineering": {"CE"},
    "Tunnel Engineering": {"CE"},
    "Water Climate Sustainability": {"CE"},
    "Water Climate and Sustainability": {"CE"},
    "Hydraulics and Water Resources": {"CE"},
    "Water Resource Engineering": {"CE"},
    "Chemical Processes Design & Intelligence": {"CH", "ME", "XE", "BT"},
    "MS Research in CSE": {"CS"},
    "MS Research in Electrical Engineering": {"EE", "EC", "IN", "CS"},
    "MS Research in Mechanical Engineering": {"ME", "PI"},
    "MS Research in Space Science & Engineering": {"EC", "EE", "XE"},
    "Robotics and Intelligent Systems": {"CS", "EE", "EC", "IN", "ME"},
    "Robotics and AI": {"CS", "EE", "EC", "IN", "ME"},
}

PLAN_DURATION_DAYS = {
    "weekly": 7,
    "monthly": 30,
    "yearly": 365,
}


def guidance_payload():
    return {
        "title": "How to apply to IIT M.Tech programs",
        "steps": [
            {"label": "Register on COAP", "detail": "Most IIT M.Tech admission offers are released through COAP after institute applications."},
            {"label": "Apply on IIT portals", "detail": "Submit separate institute/program applications before each IIT deadline."},
            {"label": "Track rounds", "detail": "Monitor COAP offer rounds and choose Accept, Retain and Wait, or Reject as applicable."},
            {"label": "Keep backups", "detail": "Use CCMT for NITs/IIITs/GFTIs and maintain a balanced preference list."},
        ],
        "timeline": [
            {"month": "Mar-Apr", "event": "Shortlist institutes and fill application forms"},
            {"month": "May-Jun", "event": "COAP offer rounds and written tests/interviews if required"},
            {"month": "Jul", "event": "Admission confirmation and reporting"},
        ],
    }


def subscription_plans_payload():
    plans = []
    for code, plan in settings.SUBSCRIPTION_PLANS.items():
        plans.append(
            {
                "code": code,
                "title": plan["title"],
                "subtitle": plan["subtitle"],
                "duration_label": plan["duration_label"],
                "amount_paise": plan["amount_paise"],
                "original_amount_paise": plan["original_amount_paise"],
                "display_amount": plan["amount_paise"] / 100,
                "display_original_amount": plan["original_amount_paise"] / 100,
                "discount_label": plan["discount_label"],
                "recommended": plan["recommended"],
            }
        )
    return plans


def metadata_payload():
    return {
        "branches": [{"value": value, "label": label} for value, label in Program._meta.get_field("branch_code").choices],
        "categories": [{"value": value, "label": label} for value, label in ApplicantSession._meta.get_field("category").choices],
        "unlock_amount": settings.UNLOCK_AMOUNT_PAISE,
        "currency": "INR",
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "subscription_plans": subscription_plans_payload(),
    }


def subscription_duration(plan_code):
    return timedelta(days=PLAN_DURATION_DAYS.get(plan_code, 7))


def payment_subscription_window(payment):
    started_at = payment.subscription_started_at or payment.updated_at or payment.created_at
    expires_at = payment.subscription_expires_at or (started_at + subscription_duration(payment.plan_code))
    return started_at, expires_at


def active_subscription_for_user(user):
    if not user or not getattr(user, "is_authenticated", False):
        return None

    now = timezone.now()
    paid_payments = (
        Payment.objects.filter(applicant_session__user=user, status=Payment.Status.PAID)
        .select_related("applicant_session")
        .order_by("-subscription_expires_at", "-updated_at")
    )

    active_subscription = None
    for payment in paid_payments:
        started_at, expires_at = payment_subscription_window(payment)
        fields_to_update = []
        if payment.subscription_started_at is None:
            payment.subscription_started_at = started_at
            fields_to_update.append("subscription_started_at")
        if payment.subscription_expires_at is None:
            payment.subscription_expires_at = expires_at
            fields_to_update.append("subscription_expires_at")
        if fields_to_update:
            payment.save(update_fields=[*fields_to_update, "updated_at"])
        if expires_at > now and (
            active_subscription is None or expires_at > active_subscription["expires_at"]
        ):
            active_subscription = {
                "plan_code": payment.plan_code,
                "started_at": started_at,
                "expires_at": expires_at,
                "payment_id": payment.id,
            }
    return active_subscription


def user_has_active_subscription(user):
    return active_subscription_for_user(user) is not None


def sync_attempt_access(attempt):
    has_access = user_has_active_subscription(attempt.user) if attempt.user_id else False
    if attempt.is_paid != has_access:
        attempt.is_paid = has_access
        attempt.save(update_fields=["is_paid", "updated_at"])
    return has_access


def csv_cutoff_rows():
    if not REAL_CUTOFFS_CSV.exists():
        return []
    with REAL_CUTOFFS_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _format_cutoff_value(value):
    if isinstance(value, Decimal):
        return format(value.normalize(), "f").rstrip("0").rstrip(".") if value != value.to_integral() else str(int(value))
    return str(value)


def _probability(score, min_score, max_score, metric_type=CutoffMetric.SCORE):
    if metric_type == CutoffMetric.MARKS:
        return "Marks-based"
    if score >= max_score:
        return "High"
    if score >= min_score:
        return "Medium"
    if score >= min_score - 45:
        return "Low"
    return "Reach"


def _match_type(selected_branch, program_branch):
    if selected_branch == program_branch:
        return "Direct"
    if program_branch in ALLIED_BRANCH_MAP.get(selected_branch, set()):
        return "Allied"
    return "Interdisciplinary"


def _program_match(program, selected_branch, include_interdisciplinary):
    if program.branch_code == selected_branch:
        return True, "Direct", f"Direct via GATE {selected_branch}"
    if not include_interdisciplinary:
        return False, None, None

    allowed_papers = PROGRAM_ELIGIBILITY_RULES.get(program.name, set())
    if selected_branch in allowed_papers:
        match_type = _match_type(selected_branch, program.branch_code)
        return True, match_type, f"Eligible via GATE {selected_branch}"
    return False, None, None


def ranked_results(score, branch, category, include_interdisciplinary=True):
    queryset = Program.objects.filter(is_active=True)
    if not include_interdisciplinary:
        queryset = queryset.filter(branch_code=branch)
    programs = list(queryset)
    if not programs:
        return []

    institute_ids = {program.institute_id for program in programs}
    institute_map = {institute.id: institute for institute in Institute.objects.filter(id__in=list(institute_ids))}

    program_ids = [program.id for program in programs]
    cutoffs_by_program = {}
    cutoff_rows = Cutoff.objects.filter(category=category, program_id__in=program_ids).order_by("program_id", "-year")
    for cutoff in cutoff_rows:
        cutoffs_by_program.setdefault(cutoff.program_id, []).append(cutoff)

    results = []
    for program in programs:
        cutoffs = cutoffs_by_program.get(program.id, [])
        if not cutoffs:
            continue
        eligible, match_type, eligibility_note = _program_match(program, branch, include_interdisciplinary)
        if not eligible:
            continue
        institute = institute_map.get(program.institute_id)
        if not institute:
            continue
        latest = cutoffs[0]
        probability = _probability(score, latest.min_score, latest.max_score, latest.metric_type)
        historical = [
            {
                "year": cutoff.year,
                "min_score": _format_cutoff_value(cutoff.min_score),
                "max_score": _format_cutoff_value(cutoff.max_score),
                "metric_type": cutoff.metric_type,
                "closing_rank": cutoff.closing_rank,
            }
            for cutoff in cutoffs
        ]
        results.append(
            {
                "iit": institute.name,
                "acronym": institute.acronym,
                "city": institute.city,
                "state": institute.state,
                "program": program.name,
                "degree": program.degree,
                "branch": program.branch_code,
                "match_type": match_type,
                "eligibility_note": eligibility_note,
                "expected_cutoff_range": f"{_format_cutoff_value(latest.min_score)}-{_format_cutoff_value(latest.max_score)}",
                "latest_cutoff": _format_cutoff_value(latest.max_score),
                "cutoff_metric": latest.metric_type,
                "cutoff_metric_label": CutoffMetric(latest.metric_type).label,
                "admission_probability": probability,
                "historical_data": historical,
                "recommendation_score": (
                    PROBABILITY_WEIGHT[probability] * 100
                    + MATCH_TYPE_WEIGHT.get(match_type, 0)
                    + institute.preference_score
                ),
            }
        )
    return sorted(results, key=lambda item: item["recommendation_score"], reverse=True)


def create_attempt(validated_data, user=None):
    attempt_data = dict(validated_data)
    include_interdisciplinary = attempt_data.pop("include_interdisciplinary", True)
    results = ranked_results(
        attempt_data["gate_score"],
        attempt_data["branch"],
        attempt_data["category"],
        include_interdisciplinary=include_interdisciplinary,
    )
    if user and user.is_authenticated:
        attempt_data["user"] = user
        if not attempt_data.get("email"):
            attempt_data["email"] = user.email
        attempt_data["is_paid"] = user_has_active_subscription(user)
    return ApplicantSession.objects.create(results_snapshot=results, **attempt_data)


def _razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return None
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _receipt_id(applicant_session):
    return f"gate{applicant_session.id.hex[:20]}"


def create_payment_order(applicant_session, plan_code):
    plan = settings.SUBSCRIPTION_PLANS[plan_code]
    amount = plan["amount_paise"]
    client = _razorpay_client()
    if client is None:
        order_id = f"order_mock_{uuid.uuid4().hex[:16]}"
        Payment.objects.create(
            applicant_session=applicant_session,
            plan_code=plan_code,
            razorpay_order_id=order_id,
            amount_paise=amount,
            raw_payload={"mode": "development_mock", "plan": plan_code},
        )
        return {
            "id": order_id,
            "amount": amount,
            "currency": "INR",
            "development_mode": True,
            "key_id": settings.RAZORPAY_KEY_ID,
            "plan": plan,
        }

    order = client.order.create(
        {
            "amount": amount,
            "currency": "INR",
            "receipt": _receipt_id(applicant_session),
            "payment_capture": 1,
            "notes": {"attempt_id": str(applicant_session.id), "plan_code": plan_code},
        }
    )
    Payment.objects.create(
        applicant_session=applicant_session,
        plan_code=plan_code,
        razorpay_order_id=order["id"],
        amount_paise=amount,
        raw_payload=order,
    )
    return {**order, "development_mode": False, "key_id": settings.RAZORPAY_KEY_ID, "plan": plan}


def verify_payment_signature(order_id, payment_id, signature):
    if order_id.startswith("order_mock_") and settings.DEBUG:
        return True
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def mark_payment_success(attempt_id, razorpay_order_id, razorpay_payment_id, razorpay_signature, payload=None):
    if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        return False, "Payment signature verification failed."

    payment = Payment.objects.get(
        applicant_session_id=attempt_id,
        razorpay_order_id=razorpay_order_id,
    )
    if (
        payment.status == Payment.Status.PAID
        and payment.subscription_expires_at
        and payment.razorpay_payment_id == razorpay_payment_id
    ):
        return True, "Subscription is already active."

    base_start = timezone.now()
    if payment.applicant_session.user_id:
        active_subscription = active_subscription_for_user(payment.applicant_session.user)
        if active_subscription and active_subscription["expires_at"] > base_start:
            base_start = active_subscription["expires_at"]
    subscription_expires_at = base_start + subscription_duration(payment.plan_code)
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.status = Payment.Status.PAID
    payment.subscription_started_at = base_start
    payment.subscription_expires_at = subscription_expires_at
    if payload:
        payment.raw_payload = payload
    payment.save(
        update_fields=[
            "razorpay_payment_id",
            "razorpay_signature",
            "status",
            "subscription_started_at",
            "subscription_expires_at",
            "raw_payload",
            "updated_at",
        ]
    )

    ApplicantSession.objects.filter(id=attempt_id).update(is_paid=True)
    return True, "Payment verified and subscription activated."


def verify_webhook_signature(raw_body, signature):
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        return settings.DEBUG
    expected = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")
