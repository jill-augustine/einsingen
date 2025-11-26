import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "insecure-secret-for-local-development"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "corsheaders",
    "einsingen",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# Vite dev mode runs on "localhost:5173" not on "127.0.0.1:5173"
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    # "http://127.0.0.1:5173",
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    # "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# TODO: Optimise these for cloud deployment in production
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = False  # Dev only. True for production
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = False  # Dev only.

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "/static/"
