import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApplicantSession, Payment
from .serializers import (
    CreateOrderSerializer,
    LoginSerializer,
    PreviewRequestSerializer,
    SignupSerializer,
    VerifyPaymentSerializer,
)
from .services import (
    active_subscription_for_user,
    create_attempt,
    create_payment_order,
    guidance_payload,
    mark_payment_success,
    metadata_payload,
    subscription_duration,
    sync_attempt_access,
    verify_webhook_signature,
)
from .throttles import PaymentThrottle, ResultsThrottle


def serialize_user(user):
    active_subscription = active_subscription_for_user(user)
    return {
        "id": str(user.id),
        "full_name": user.first_name or user.get_full_name() or user.username,
        "email": user.email,
        "subscription": (
            {
                "plan_code": active_subscription["plan_code"],
                "started_at": active_subscription["started_at"],
                "expires_at": active_subscription["expires_at"],
            }
            if active_subscription
            else None
        ),
    }


def attach_attempt_to_user(attempt, user):
    if attempt.user_id and attempt.user_id != user.id:
        raise PermissionDenied("This result belongs to another account.")
    updates = []
    if attempt.user_id is None:
        attempt.user = user
        updates.append("user")
    if not attempt.email and user.email:
        attempt.email = user.email
        updates.append("email")
    if updates:
        attempt.save(update_fields=[*updates, "updated_at"])
    sync_attempt_access(attempt)
    return attempt


@api_view(["GET"])
def health(_request):
    return Response({"status": "ok", "service": "gate-advisor"})


@api_view(["GET"])
def metadata(_request):
    return Response(metadata_payload())


@api_view(["GET"])
def guidance(_request):
    return Response(guidance_payload())


class ResultsPreviewView(APIView):
    throttle_classes = [ResultsThrottle]
    throttle_scope = "results"

    def post(self, request):
        serializer = PreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = create_attempt(serializer.validated_data, request.user)
        is_paid = sync_attempt_access(attempt)
        preview = attempt.results_snapshot if is_paid else attempt.results_snapshot[:3]
        return Response(
            {
                "attempt": {
                    "id": attempt.id,
                    "gate_score": attempt.gate_score,
                    "branch": attempt.branch,
                    "category": attempt.category,
                    "rank": attempt.rank,
                    "is_paid": is_paid,
                },
                "results": preview,
                "locked_count": 0 if is_paid else max(len(attempt.results_snapshot) - len(preview), 0),
                "total_matches": len(attempt.results_snapshot),
                "guidance": guidance_payload(),
            },
            status=status.HTTP_201_CREATED,
        )


class ResultsDetailView(APIView):
    throttle_classes = [ResultsThrottle]
    throttle_scope = "results"

    def get(self, request, attempt_id):
        attempt = get_object_or_404(ApplicantSession, id=attempt_id)
        if request.user.is_authenticated:
            attach_attempt_to_user(attempt, request.user)
        is_paid = sync_attempt_access(attempt)
        results = attempt.results_snapshot if is_paid else attempt.results_snapshot[:3]
        return Response(
            {
                "attempt": {
                    "id": attempt.id,
                    "gate_score": attempt.gate_score,
                    "branch": attempt.branch,
                    "category": attempt.category,
                    "rank": attempt.rank,
                    "is_paid": is_paid,
                },
                "results": results,
                "locked_count": 0 if is_paid else max(len(attempt.results_snapshot) - len(results), 0),
                "total_matches": len(attempt.results_snapshot),
                "guidance": guidance_payload(),
            }
        )


class CreateOrderView(APIView):
    throttle_classes = [PaymentThrottle]
    throttle_scope = "payments"
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = get_object_or_404(ApplicantSession, id=serializer.validated_data["attempt_id"])
        attach_attempt_to_user(attempt, request.user)
        order = create_payment_order(attempt, serializer.validated_data["plan_code"])
        return Response({"order": order})


class VerifyPaymentView(APIView):
    throttle_classes = [PaymentThrottle]
    throttle_scope = "payments"
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = get_object_or_404(ApplicantSession, id=serializer.validated_data["attempt_id"])
        attach_attempt_to_user(attempt, request.user)
        ok, message = mark_payment_success(**serializer.validated_data, payload=request.data)
        return Response(
            {"ok": ok, "message": message},
            status=status.HTTP_200_OK if ok else status.HTTP_400_BAD_REQUEST,
        )


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": serialize_user(user)}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": serialize_user(user)})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"user": serialize_user(request.user)})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = Token.objects.filter(user=request.user, key=getattr(request.auth, "key", "")).first()
        if token:
            token.delete()
        return Response({"ok": True})


@csrf_exempt
def razorpay_webhook(request):
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not verify_webhook_signature(request.body, signature):
        return JsonResponse({"ok": False, "message": "Invalid signature"}, status=400)

    payload = json.loads(request.body.decode() or "{}")
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = payment_entity.get("order_id")
    payment_id = payment_entity.get("id")

    if payload.get("event") == "payment.captured" and order_id and payment_id:
        payment = Payment.objects.filter(razorpay_order_id=order_id).first()
        if payment:
            if (
                payment.status == Payment.Status.PAID
                and payment.subscription_expires_at
                and payment.razorpay_payment_id == payment_id
            ):
                return JsonResponse({"ok": True})
            base_start = timezone.now()
            if payment.applicant_session.user_id:
                active_subscription = active_subscription_for_user(payment.applicant_session.user)
                if active_subscription and active_subscription["expires_at"] > base_start:
                    base_start = active_subscription["expires_at"]
            expires_at = base_start + subscription_duration(payment.plan_code)
            payment.status = Payment.Status.PAID
            payment.razorpay_payment_id = payment_id
            payment.subscription_started_at = base_start
            payment.subscription_expires_at = expires_at
            payment.raw_payload = payload
            payment.save(
                update_fields=[
                    "status",
                    "razorpay_payment_id",
                    "subscription_started_at",
                    "subscription_expires_at",
                    "raw_payload",
                    "updated_at",
                ]
            )
            ApplicantSession.objects.filter(id=payment.applicant_session_id).update(is_paid=True)

    return JsonResponse({"ok": True})
