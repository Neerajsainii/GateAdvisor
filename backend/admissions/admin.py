from django.contrib import admin

from .models import ApplicantSession, Cutoff, Institute, Payment, Program


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ("acronym", "name", "city", "preference_score")
    search_fields = ("name", "acronym", "city")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "institute", "branch_code", "degree", "is_active")
    list_filter = ("branch_code", "degree", "is_active", "institute")
    search_fields = ("name", "institute__name", "institute__acronym")


@admin.register(Cutoff)
class CutoffAdmin(admin.ModelAdmin):
    list_display = ("program", "category", "year", "min_score", "max_score", "closing_rank")
    list_filter = ("category", "year", "program__branch_code", "program__institute")
    search_fields = ("program__name", "program__institute__name")


@admin.register(ApplicantSession)
class ApplicantSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "gate_score", "branch", "category", "rank", "is_paid", "created_at")
    list_filter = ("branch", "category", "is_paid")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "razorpay_order_id",
        "status",
        "plan_code",
        "amount_paise",
        "subscription_expires_at",
        "applicant_session",
        "created_at",
    )
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at")
