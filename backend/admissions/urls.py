from django.urls import path

from .views import (
    CreateOrderView,
    LoginView,
    LogoutView,
    MeView,
    ResultsDetailView,
    ResultsPreviewView,
    SignupView,
    VerifyPaymentView,
    AdminLoginView,
    AdminDashboardView,
    guidance,
    health,
    metadata,
    razorpay_webhook,
)


urlpatterns = [
    path("auth/signup/", SignupView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("health/", health),
    path("metadata/", metadata),
    path("guidance/", guidance),
    path("results/preview/", ResultsPreviewView.as_view()),
    path("results/<uuid:attempt_id>/", ResultsDetailView.as_view()),
    path("payments/create-order/", CreateOrderView.as_view()),
    path("payments/verify/", VerifyPaymentView.as_view()),
    path("payments/razorpay/webhook/", razorpay_webhook),
    path("auth/admin-login/", AdminLoginView.as_view()),
    path("admin/users/", AdminDashboardView.as_view()),
]
