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
DEBUG = True

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

STATIC_URL = 'static/'

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
DEBUG = os.environ.get("DEBUG", "False").lower() in ("1","true","yes")

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


TEMPLATES[0]['OPTIONS']['builtins'] = ['myApp.templatetags.money']


PRICE_SOURCE_CURRENCY = "JOD"

