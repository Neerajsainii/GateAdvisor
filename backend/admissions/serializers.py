from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import ApplicantSession, Branch, Category


User = get_user_model()


class PreviewRequestSerializer(serializers.Serializer):
    gate_score = serializers.IntegerField(min_value=0, max_value=1000)
    branch = serializers.ChoiceField(choices=Branch.choices)
    category = serializers.ChoiceField(choices=Category.choices)
    include_interdisciplinary = serializers.BooleanField(required=False, default=True)
    rank = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class ApplicantSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantSession
        fields = ("id", "gate_score", "branch", "category", "rank", "email", "is_paid", "created_at")
        read_only_fields = ("id", "is_paid", "created_at")


class CreateOrderSerializer(serializers.Serializer):
    attempt_id = serializers.UUIDField(required=False, allow_null=True)
    plan_code = serializers.ChoiceField(choices=["weekly", "monthly", "yearly", "custom"])
    custom_days = serializers.IntegerField(min_value=1, max_value=3650, required=False, allow_null=True)

    def validate(self, attrs):
        plan_code = attrs["plan_code"]
        custom_days = attrs.get("custom_days")
        if plan_code == "custom" and not custom_days:
            raise serializers.ValidationError({"custom_days": "Enter the number of days to add."})
        if plan_code != "custom":
            attrs["custom_days"] = None
        return attrs


class VerifyPaymentSerializer(serializers.Serializer):
    attempt_id = serializers.UUIDField()
    razorpay_order_id = serializers.CharField(max_length=120)
    razorpay_payment_id = serializers.CharField(max_length=120)
    razorpay_signature = serializers.CharField(max_length=256)


class SignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def create(self, validated_data):
        full_name = validated_data["full_name"].strip()
        email = validated_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=full_name,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        user = authenticate(username=email, password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        attrs["email"] = email
        return attrs
