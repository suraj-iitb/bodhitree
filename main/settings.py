"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import logging.config
import os
import sys
from configparser import ConfigParser
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Read configurations from settings.ini file
config = ConfigParser()
config.read(os.path.join(BASE_DIR, "main/settings.ini"))

SECRET_KEY = config["server"]["secret_key"]

DEBUG = config["server"].getboolean("debug")

ALLOWED_HOSTS = config["server"]["allowed_hosts"]

TEST = "test" in sys.argv

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "django_filters",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
    # Our apps
    "discussion_forum",
    "cribs",
    "registration",
    "course",
    "document",
    "email_notices",
    "leaderboard",
    "programming_assignments",
    "quiz",
    "stats",
    "subjective_assignments",
    "video",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG and not TEST:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "main.urls"

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

WSGI_APPLICATION = "main.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": config["database"]["engine"],
        "NAME": config["database"]["db_name"],
        "USER": config["database"]["user"],
        "PASSWORD": config["database"]["password"],
        "HOST": config["database"]["host"],
        "PORT": config["database"]["port"],
    }
}

# Email
EMAIL_HOST = config["email"]["host"]
EMAIL_PORT = config["email"]["port"]
EMAIL_HOST_USER = config["email"]["user"]
EMAIL_HOST_PASSWORD = config["email"]["password"]
EMAIL_BACKEND = config["email"]["backend"]
EMAIL_USE_TLS = config["email"]["use_tls"]
EMAIL_SUBJECT_PREFIX = config["email"]["subject_prefix"]
EMAIL_DOMAIN = config["email"]["domain"]
EMAIL_REPLY_TO = config["email"]["reply_to"]

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
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

# Django rest framework
DEFAULT_RENDERER_CLASSES = [
    "rest_framework.renderers.JSONRenderer",
]

if DEBUG:
    DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + [
        "rest_framework.renderers.BrowsableAPIRenderer",
    ]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "200/min",
    },
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": DEFAULT_RENDERER_CLASSES,
    # For testing
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# CORS hosts
CORS_ALLOWED_ORIGINS = [
    "{protocol}://{ip}:{port}".format(
        protocol=config["app"]["protocol"],
        ip=config["app"]["ip"],
        port=config["app"]["port"],
    )
]

# Django debug toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

# Simple JWT
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT",),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s [%(asctime)s] [%(name)s] [%(module)s]"
            "[Process:%(process)d] [Thread:%(thread)d] %(message)s",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["require_debug_true"],
        },
        "file_django": {
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "main/logs/django.log"),
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["file_django"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
LOGGING_CONFIG = None
logging.config.dictConfig(LOGGING)

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

# User uploaded files locations
if TEST:
    MEDIA_ROOT = os.path.join(BASE_DIR, "main/test/")
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, "main/data/")

# User model
AUTH_USER_MODEL = "registration.User"

# Type of auto-created primary keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Max charfield limit
MAX_CHARFIELD_LENGTH = 100

# Additional fixtures directories
FIXTURE_DIRS = [os.path.join(BASE_DIR, "main/fixtures")]
