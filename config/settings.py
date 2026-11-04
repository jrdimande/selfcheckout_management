import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env(key, default=None):
    return os.getenv(key, default)


TESTING = "test" in sys.argv
DEBUG = env("DEBUG", "False").lower() in ("1", "true", "yes")
SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG or TESTING:
        SECRET_KEY = "dev-insecure-key-change-me"
    else:
        raise ImproperlyConfigured("Defina SECRET_KEY no ficheiro .env")
ALLOWED_HOSTS = [h.strip() for h in env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
CURRENCY = env("CURRENCY", "")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.core",
    "apps.accounts",
    "apps.audit",
    "apps.customers",
    "apps.products",
    "apps.sales",
    "apps.payments",
    "apps.dashboard",
    "apps.reports",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "apps.accounts.permissions.roles",
    ]},
}]

# ---------------------------------------------------------------------------
# Bases de dados
#   "selfcheckout" -> base MySQL PARTILHADA com a app Java (models managed=False,
#                     nunca recebe migrations).
#   "default"      -> base interna do Django (utilizadores, sessões, auditoria).
# ---------------------------------------------------------------------------
DATABASE_ROUTERS = ["config.db_router.SelfCheckoutRouter"]

if TESTING:
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        "selfcheckout": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
    }
    TEST_RUNNER = "config.test_runner.SchemaRunner"
else:
    DATABASES = {
        "selfcheckout": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME", "self_checkout"),
            "HOST": env("DB_HOST", "192.168.10.44"),
            "PORT": env("DB_PORT", "3306"),
            "USER": env("DB_USER", ""),
            "PASSWORD": env("DB_PASSWORD", ""),
            "CONN_MAX_AGE": 60,
            "OPTIONS": {"charset": "utf8mb4", "connect_timeout": 10},
        }
    }
    if env("ADMIN_DB_ENGINE", "sqlite").lower() == "mysql":
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("ADMIN_DB_NAME", "self_checkout_admin"),
            "HOST": env("ADMIN_DB_HOST", env("DB_HOST", "")),
            "PORT": env("ADMIN_DB_PORT", "3306"),
            "USER": env("ADMIN_DB_USER", env("DB_USER", "")),
            "PASSWORD": env("ADMIN_DB_PASSWORD", env("DB_PASSWORD", "")),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    else:
        DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "admin_data.sqlite3"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt"
TIME_ZONE = env("TIME_ZONE", "Africa/Maputo")
USE_I18N = True
USE_TZ = False  # as colunas DATETIME do MySQL são "naive"; evita conversões

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "accounts:login"
SESSION_COOKIE_AGE = 60 * 60 * 8
SESSION_COOKIE_HTTPONLY = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"]
    + (["rest_framework.renderers.BrowsableAPIRenderer"] if DEBUG else []),
    "EXCEPTION_HANDLER": "apps.api.exceptions.handler",
}

(BASE_DIR / "logs").mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"std": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "std"},
        "file": {"class": "logging.FileHandler", "filename": BASE_DIR / "logs" / "app.log", "formatter": "std"},
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}
