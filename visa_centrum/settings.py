"""
Django settings for the Visa Centrum XBA website.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# SECURITY WARNING: set a real, secret DJANGO_SECRET_KEY in .env before deploying!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-me-before-deploying",
)

DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()
]

# A tunnel (cloudflared, ngrok, ...) terminates TLS and forwards to this app
# as plain HTTP, so Django would otherwise think every request is insecure.
# Trust the proxy's X-Forwarded-Proto header instead.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ALLOWED_HOSTS alone lets the request through, but Django's CSRF check
# (needed for the admin login form, the contact form, the language switcher)
# separately requires the request's Origin to be explicitly trusted here —
# otherwise POSTs from a tunnel domain are rejected with 403 even though the
# page itself loads fine. `https://*.trycloudflare.com` covers cloudflared's
# quick-tunnel domain, which is different every time it's started.
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS", "https://*.trycloudflare.com"
    ).split(",") if o.strip()
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "vacancies",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "visa_centrum.urls"

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
                "core.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "visa_centrum.wsgi.application"


# Database — SQLite by default (zero setup); point DATABASE_URL-style
# settings at Postgres yourself in production if you prefer, same as the
# sibling visa-centrum-bot project.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization.
#
# This project does NOT use Django's gettext/.po machinery — there is no
# compiled catalog. `LocaleMiddleware` + `i18n_patterns` only handle URL
# prefixes and remembering the visitor's chosen language (session/cookie);
# the actual site copy is looked up directly from core/translations.py via
# the `T` template variable (see core/context_processors.py). Vacancy
# CONTENT is admin-authored per language on the Vacancy model itself.
LANGUAGE_CODE = "uz"

LANGUAGES = [
    ("uz", "O'zbek"),
    ("de", "Deutsch"),
    ("en", "English"),
    ("ru", "Русский"),
]

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
