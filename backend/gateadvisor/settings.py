from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
] + ["169.254.130.4"]  # Azure internal health probe

INSTALLED_APPS = [
    "gateadvisor.apps.MongoAdminConfig",
    "gateadvisor.apps.MongoAuthConfig",
    "gateadvisor.apps.MongoContentTypesConfig",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "admissions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gateadvisor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gateadvisor.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        "NAME": os.getenv("MONGODB_NAME", "test_userss"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
MIGRATION_MODULES = {
    "admin": "mongo_migrations.admin",
    "auth": "mongo_migrations.auth",
    "contenttypes": "mongo_migrations.contenttypes",
    "admissions": "mongo_migrations.admissions",
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True 
REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # ← add this
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "admissions.throttles.ResultsThrottle",
        "admissions.throttles.PaymentThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "300/hour",
        "user": "1000/hour",
        "results": "60/hour",
        "payments": "30/hour",
    },
}

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
UNLOCK_AMOUNT_PAISE = int(os.getenv("UNLOCK_AMOUNT_PAISE", "1000"))
SUBSCRIPTION_PLANS = {
    "weekly": {
        "code": "weekly",
        "title": "Weekly Pass",
        "subtitle": "Quick shortlist access",
        "duration_label": "7 days access",
        "amount_paise": int(os.getenv("PLAN_WEEKLY_PAISE", "1000")),
        "original_amount_paise": int(os.getenv("PLAN_WEEKLY_ORIGINAL_PAISE", "10000")),
        "discount_label": "90% OFF",
        "recommended": False,
    },
    "monthly": {
        "code": "monthly",
        "title": "Monthly Pass",
        "subtitle": "Steady prep companion",
        "duration_label": "30 days access",
        "amount_paise": int(os.getenv("PLAN_MONTHLY_PAISE", "4900")),
        "original_amount_paise": int(os.getenv("PLAN_MONTHLY_ORIGINAL_PAISE", "4900")),
        "discount_label": "",
        "recommended": False,
    },
    "yearly": {
        "code": "yearly",
        "title": "Yearly Pass",
        "subtitle": "Best value for full prep",
        "duration_label": "365 days access",
        "amount_paise": int(os.getenv("PLAN_YEARLY_PAISE", "9900")),
        "original_amount_paise": int(os.getenv("PLAN_YEARLY_ORIGINAL_PAISE", "99900")),
        "discount_label": "90% OFF",
        "recommended": True,
    },
}
CUSTOM_SUBSCRIPTION_DAILY_PRICE_PAISE = int(os.getenv("CUSTOM_SUBSCRIPTION_DAILY_PRICE_PAISE", "500"))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
