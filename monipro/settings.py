import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Zabbix Configuration
ZABBIX_API_URL = os.getenv("ZABBIX_API_URL", "https://zx.brothersit.dev")
ZABBIX_ADMIN_USER = os.getenv("ZABBIX_ADMIN_USER", "Admin")
ZABBIX_ADMIN_PASSWORD = os.getenv("ZABBIX_ADMIN_PASSWORD", "zabbix")
ZABBIX_DEFAULT_PASSWORD = os.getenv("ZABBIX_DEFAULT_PASSWORD", "nochangeatall")


# ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
# CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
# CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
# CORS_ALLOW_METHODS = os.environ.get("CORS_ALLOW_METHODS", "").split(",")
# CORS_ALLOW_CREDENTIALS = os.environ.get("CORS_ALLOW_CREDENTIALS") == "True"
# CORS_ALLOW_HEADERS = os.environ.get("CORS_ALLOW_HEADERS", "").split(",")

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "monipro.brothersit.dev", "192.168.10.118"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "https://monipro.brothersit.dev",
]

# Update CORS and CSRF settings
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read the CSRF token
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "https://monipro.brothersit.dev",
]
CORS_ALLOW_ALL_ORIGINS = False  # Add this line
CORS_ORIGIN_ALLOW_ALL = False  # Add this line

# Add these settings
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]
CORS_PREFLIGHT_MAX_AGE = 86400
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "https://monipro.brothersit.dev",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # custome apps
    "users",
    "customers",
    "subscription",
    "zabbixproxy",
    "jobs",
    "agents",
    "item_types",
    "scripts",
    "payment",
    # therd party apps
    "corsheaders",
    "rest_framework",
    "drf_yasg",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "social_django",
    "allauth.headless",
    "django_cron",
]
AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "middleware.authmiddleware.JWTAuthenticationMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}


JWT_AUTH = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("SECRET_KEY"),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "EXCLUDED_URL_NAMES": [
        "login",
        "initial-register",
        "swagger",
        "private-register",
        "password-forgot",
        "password-reset",
        "google-exchange",
    ],
    "EXCLUDED_PATHS": [
        "/api/login/",
        "/api/initial-register/",
        "/swagger/",
        "/admin/",
        "/api/plans/",
        "/api/verify/",
        "/api/vm-info/",
        "/api/private-register/",
        "/api/password-forgot/",
        "/api/password-reset/",
        "/api/google-exchange/",
        "/api/deploy/",
        "/api/token/refresh/",
        "/api/token/",
    ],
    "COOKIE_SETTINGS": {
        "ACCESS_TOKEN_NAME": "access_token",
        "REFRESH_TOKEN_NAME": "refresh_token",
        "HTTPONLY": True,
        "SECURE": False,
        "SAMESITE": "Lax",
        "ACCESS_MAX_AGE": 60480,
        "REFRESH_MAX_AGE": 604800,
    },
}


ROOT_URLCONF = "monipro.urls"

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

WSGI_APPLICATION = "monipro.wsgi.application"

# FOR CONTAINERIZATION
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "moniprodb"),
        "USER": os.getenv("POSTGRES_USER", "moniprouser"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "monipropass"),
        "HOST": os.getenv("DATABASE_HOST", "moni_pro"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}


# FOR TEST
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("REMOTE_DB_NAME"),
#         "USER": os.getenv("REMOTE_DB_USER"),
#         "PASSWORD": os.getenv("REMOTE_DB_PASSWORD"),
#         "HOST": os.getenv("REMOTE_DB_HOST"),
#         "PORT": os.getenv("REMOTE_DB_PORT"),
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


PASSWORD_RESET_TIMEOUT = 1800

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
VERFICATION_URL = "https://monipro.brothersit.dev/verification"
LOGIN_URL = "https://monipro.brothersit.dev/auth"


ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": "289478844187-2lckh4oovv3jied47060dajl12g83e8b.apps.googleusercontent.com",
            "secret": "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",
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "REDIRECT_URI": "http://localhost:8000/api/auth/google/callback/",
    },
    "github": {
        "APP": {
            "client_id": "Ov23lilbz1w8uUzFXM9n",
            "secret": "94398e32cbd5847690300ad14a93e45e50039606",
            "key": "",
        },
        "SCOPE": ["user:email"],
        "REDIRECT_URI": "http://localhost:8000/api/auth/github/callback/",
    },
}
LOGIN_REDIRECT_URL = "google-callback"
SOCIALACCOUNT_LOGIN_ON_GET = True
REDIRECT_URL = "http://localhost:5173/social/auth/google/callback"
# REDIRECT_URL = "https://monipro.brothersit.dev/social/auth/google/callback"

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
        "zabbix_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "zabbix.log"),
            "formatter": "default",
        },
        "django_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "django.log"),
            "formatter": "default",
        },
        "ansibal_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "ansibal.log"),
            "formatter": "default",
        },
        "celery_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "celery.log"),
            "formatter": "default",
        },
        "sms_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "sms.log"),
            "formatter": "default",
        },
        "payment_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "payment.log"),
            "formatter": "default",
        },
    },
    "loggers": {
        "zabbix": {
            "handlers": ["zabbix_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["django_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "ansibal": {
            "handlers": ["ansibal_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "celery": {
            "handlers": ["celery_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "sms": {
            "handlers": ["sms_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "payment": {
            "handlers": ["payment_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

CRONJOBS = [("0 0 * * *", "jobs.functions.DeleteOldTokensCronJob")]

ZABBIX_PLAYBOOK_PATH = os.path.join(
    BASE_DIR,
    "zabbixproxy",
    "automation_functions",
    "ansibal_playbooks",
    "zabbix-playbook.yml",
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monipro.settings")
# Update Redis connection settings to use the service name instead of localhost
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

# Additional Celery settings
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


CHAPA_TRANSACTION_MODEL = "payment.ChapaTransaction"
