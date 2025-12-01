from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
    load_dotenv(BASE_DIR / '.env.local', override=True)
except Exception:
    # If python-dotenv isn't installed, we just rely on OS env vars.
    pass

# Helpers for clean env parsing
def env_bool(key: str, default: bool = False) -> bool:
    return str(os.environ.get(key, default)).lower() in ('1', 'true', 't', 'yes', 'y', 'on')

def env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#2^w$lur2d&t90sltvbcsjfl+bi=l3(=zea+_9@ste85h21ioo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = [
    'sharpecom-production.up.railway.app',
    'www.sharphair.shop',
    'sharphair.shop',
    '127.0.0.1',
    'localhost',
]


CSRF_TRUSTED_ORIGINS = [
    'https://sharpecom-production.up.railway.app',
    'https://www.sharphair.shop',
    'https://sharphair.shop',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myApp',
    'anymail',  # for SendGrid HTTPS API
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',   # keep this first for sessions
    'myApp.middleware.CurrencyMiddleware',                 # ← ADD THIS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]


ROOT_URLCONF = 'myProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myApp.context_processors.cart',
                'myApp.context_processors.sitewide_promo',
                'myApp.context_processors.dashboard_counts',
            ],
        },
    },
]


SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE    = "Lax"
# If you serve over HTTPS in prod, set these True in prod:
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE    = env_bool("CSRF_COOKIE_SECURE", False)



WSGI_APPLICATION = 'myProject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Database configuration - Always use PostgreSQL from DATABASE_URL
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in your .env file or environment variables."
    )

# Always use PostgreSQL from DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Log database configuration
db_config = DATABASES['default']
print("=" * 60)
print("DATABASE CONFIGURATION:")
print(f"  Engine: {db_config.get('ENGINE', 'Unknown')}")
print(f"  Name: {db_config.get('NAME', 'Unknown')}")
print(f"  Host: {db_config.get('HOST', 'Unknown')}")
print(f"  Port: {db_config.get('PORT', 'Unknown')}")
print(f"  User: {db_config.get('USER', 'Unknown')}")
print("=" * 60)

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = "/static/"

# Where YOUR project-level assets live (optional but common)
STATICFILES_DIRS = [BASE_DIR / "static"]

# Where collectstatic puts files (mainly for prod)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Static file caching with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise configuration for better performance
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files
WHITENOISE_USE_FINDERS = True  # Use Django's static file finders

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'myApp.context_processors.cart',
]

# ---------------------------
# EMAIL CONFIG — Prefer SendGrid (HTTPS). Fallback to Gmail SMTP locally. Else console.
# ---------------------------
# ---------------------------
# EMAIL CONFIG — Primary: Resend (HTTPS API). Fallbacks: SMTP (optional) → console.
# ---------------------------
import os

# If you still use Django's send_mail elsewhere, keep it from tripping in prod:


# Not strictly required for Resend (we’ll call the HTTP API), but safe defaults:
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend" if DEBUG
    else "django.core.mail.backends.dummy.EmailBackend"
)

# Useful for emails you render or any fallback usage
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL") or os.environ.get("RESEND_FROM")

# Resend config (used by your utility function)
RESEND = {
    "API_KEY": os.environ.get("RESEND_API_KEY"),
    "FROM": os.environ.get("RESEND_FROM"),
    "REPLY_TO": os.environ.get("RESEND_REPLY_TO"),
    "BASE_URL": os.environ.get("RESEND_BASE_URL", "https://api.resend.com"),
}


LOGIN_URL = 'dashboard_login'


TEMPLATES[0]['OPTIONS']['builtins'] = [
    'myApp.templatetags.money',
    'myApp.templatetags.shop_extras',  
    'myApp.templatetags.form_extras',
]


PRICE_SOURCE_CURRENCY = "JOD"

import os

WASSEL = {
    "EMAIL": os.getenv("WASSEL_EMAIL", ""),
    "PASSWORD": os.getenv("WASSEL_PASSWORD", ""),
    "COMPANY_STORE_ID": os.getenv("WASSEL_COMPANY_STORE_ID", "13"),
    "TIMEOUT": int(os.getenv("WASSEL_TIMEOUT", 20)),
    "WEBHOOK_SHARED_SECRET": os.getenv("WASSEL_WEBHOOK_SHARED_SECRET", ""),
}


# settings.py
import os
ZOHO = {
    "CLIENT_ID": os.getenv("ZOHO_CLIENT_ID"),
    "CLIENT_SECRET": os.getenv("ZOHO_CLIENT_SECRET"),
    "REFRESH_TOKEN": os.getenv("ZOHO_REFRESH_TOKEN"),
    "ORG_ID": os.getenv("ZOHO_ORG_ID"),
    "BASE": os.getenv("ZOHO_BASE", "https://www.zohoapis.com"),
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.request": {"handlers": ["console"], "level": "ERROR"},
        "django.template": {"handlers": ["console"], "level": "ERROR"},
    },
}

# ============================================================================
# Cloudinary Configuration
# ============================================================================
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', ''),
        api_key=os.getenv('CLOUDINARY_API_KEY', ''),
        api_secret=os.getenv('CLOUDINARY_API_SECRET', ''),
        secure=True
    )
except Exception as e:
    print(f"Warning: Cloudinary not configured: {e}")
