import environ
import os
from pathlib import Path
from datetime import timedelta

import environ
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ""),
    MASTER_DATABASE_URL=(str, ""),
    TENANT_DATABASE_URL=(str, ""),
    JWT_SECRET_KEY=(str, ""),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CORS_ALLOW_ALL_ORIGINS=(bool, False),
)

# Now assign
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ------------------------------
# Apps
# ------------------------------
SHARED_APPS = [
    "django_tenants",  # MUST be first
    "master_db",       # Shared apps: User, Client, Domain
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "core",
]

TENANT_APPS = [
    "tenant_db",       # Tenant apps: Product, Order, etc.
    "django.contrib.contenttypes",
    "django.contrib.auth",      # Permissions inside tenant schemas
    "django.contrib.sessions",  # Optional
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

# ------------------------------
# Tenants
# ------------------------------
TENANT_MODEL = "master_db.Client"
TENANT_DOMAIN_MODEL = "master_db.Domain"
PUBLIC_SCHEMA_NAME = "public"
TENANT_DATABASE_ALIAS = "tenant_db"

# ------------------------------
# Middleware
# ------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------
# Routers
# ------------------------------
DATABASE_ROUTERS = [
    "sampleDjango.routers.CustomTenantSyncRouter",
    "django_tenants.routers.TenantSyncRouter",     # required by django-tenants
]

# ------------------------------
# Auth
# ------------------------------
AUTH_USER_MODEL = "master_db.User"

# ------------------------------
# Databases
# ------------------------------
DATABASES = {
    "default": env.db("MASTER_DATABASE_URL"),   # public/master DB
    "tenant_db": env.db("TENANT_DATABASE_URL"), # tenant DB
}

# Correct engines
DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"
DATABASES["tenant_db"]["ENGINE"] = "django_tenants.postgresql_backend"

# ------------------------------
# URLs / WSGI
# ------------------------------
ROOT_URLCONF = "sampleDjango.urls"
WSGI_APPLICATION = "sampleDjango.wsgi.application"

# ------------------------------
# Templates
# ------------------------------
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

# ------------------------------
# Password validators
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------
# Internationalization
# ------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------
# Static files
# ------------------------------
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------
# REST Framework & JWT
# ------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SECRET_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ------------------------------
# CORS
# ------------------------------
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS")
