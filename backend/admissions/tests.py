from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import ApplicantSession, Category, Cutoff, Institute, Program


@override_settings(DEBUG=True, RAZORPAY_KEY_ID="", RAZORPAY_KEY_SECRET="")
class AdmissionsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="supersecret123",
            first_name="Test User",
        )
        self.token = Token.objects.create(user=self.user)
        institute = Institute.objects.create(
            name="IIT Test",
            acronym="IITT",
            city="Test City",
            state="Test State",
            preference_score=80,
        )
        programs = [
            Program.objects.create(institute=institute, name="Computer Science and Engineering", branch_code="CS"),
            Program.objects.create(institute=institute, name="Artificial Intelligence", branch_code="CS"),
            Program.objects.create(institute=institute, name="Data Engineering", branch_code="CS"),
            Program.objects.create(institute=institute, name="Software Systems", branch_code="CS"),
            Program.objects.create(institute=institute, name="Biomedical Engineering", branch_code="BT"),
        ]
        for index, program in enumerate(programs, start=1):
            Cutoff.objects.create(
                program=program,
                category=Category.GENERAL,
                year=2025,
                min_score=500 + index,
                max_score=600 + index,
            )

    def test_preview_returns_limited_results(self):
        response = self.client.post(
            "/api/results/preview/",
            {"gate_score": 760, "branch": "CS", "category": "GENERAL"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["locked_count"], 2)

    def test_interdisciplinary_toggle_includes_cross_branch_programs(self):
        preview = self.client.post(
            "/api/results/preview/",
            {"gate_score": 760, "branch": "CS", "category": "GENERAL", "include_interdisciplinary": True},
            format="json",
        )
        attempt_id = preview.data["attempt"]["id"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        order = self.client.post(
            "/api/payments/create-order/",
            {"attempt_id": attempt_id, "plan_code": "weekly"},
            format="json",
        )
        self.client.post(
            "/api/payments/verify/",
            {
                "attempt_id": attempt_id,
                "razorpay_order_id": order.data["order"]["id"],
                "razorpay_payment_id": "pay_mock_interdisciplinary",
                "razorpay_signature": "debug",
            },
            format="json",
        )
        response = self.client.get(f"/api/results/{attempt_id}/")
        result_programs = [row["program"] for row in response.data["results"]]
        self.assertIn("Biomedical Engineering", result_programs)

    def test_mock_payment_unlocks_full_results_in_debug(self):
        preview = self.client.post(
            "/api/results/preview/",
            {"gate_score": 760, "branch": "CS", "category": "GENERAL"},
            format="json",
        )
        attempt_id = preview.data["attempt"]["id"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        order = self.client.post(
            "/api/payments/create-order/",
            {"attempt_id": attempt_id, "plan_code": "weekly"},
            format="json",
        )
        order_id = order.data["order"]["id"]

        verify = self.client.post(
            "/api/payments/verify/",
            {
                "attempt_id": attempt_id,
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_mock",
                "razorpay_signature": "debug",
            },
            format="json",
        )

        self.assertEqual(verify.status_code, 200)
        self.assertTrue(ApplicantSession.objects.get(id=attempt_id).is_paid)

    def test_create_order_requires_login(self):
        preview = self.client.post(
            "/api/results/preview/",
            {"gate_score": 760, "branch": "CS", "category": "GENERAL"},
            format="json",
        )

        response = self.client.post(
            "/api/payments/create-order/",
            {"attempt_id": preview.data["attempt"]["id"], "plan_code": "weekly"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_signup_and_me(self):
        signup_client = APIClient()
        signup = signup_client.post(
            "/api/auth/signup/",
            {"full_name": "Fresh User", "email": "fresh@example.com", "password": "complexpass123"},
            format="json",
        )

        self.assertEqual(signup.status_code, 201)
        token = signup.data["token"]

        signup_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me = signup_client.get("/api/auth/me/")

        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["user"]["email"], "fresh@example.com")
