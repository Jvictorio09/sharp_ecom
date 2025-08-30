from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(BASE_DIR / ".env.local", override=True)
except Exception:
    # If python-dotenv isn't installed, we just rely on OS env vars.
    pass

# Helpers for clean env parsing
def env_bool(key: str, default: bool = False) -> bool:
    return str(os.environ.get(key, default)).lower() in ("1", "true", "t", "yes", "y", "on")

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
    'sharpecom-production.up.railway.app',  # Railway production
    '127.0.0.1',                            # Localhost loopback
    'localhost',                            # Localhost name
]

CSRF_TRUSTED_ORIGINS = [
    "https://sharpecom-production.up.railway.app",
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
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [BASE_DIR / "templates"],
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

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "myApp.context_processors.cart",
]

# ---------------------------
# EMAIL CONFIG — Prefer SendGrid (HTTPS). Fallback to Gmail SMTP locally. Else console.
# ---------------------------
import warnings

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "").strip()
EMAIL_ALLOW_SMTP = env_bool("EMAIL_ALLOW_SMTP", False)  # set to 1 locally if you want Gmail SMTP

if SENDGRID_API_KEY:
    # Railway-safe: HTTPS API (no blocked ports)
    EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
    ANYMAIL = {"SENDGRID_API_KEY": SENDGRID_API_KEY}

    # Silence Anymail's SendGrid support warning noise
    try:
        from anymail.exceptions import AnymailNotSupportedWarning
        warnings.filterwarnings("ignore", category=AnymailNotSupportedWarning)
    except Exception:
        pass

elif EMAIL_ALLOW_SMTP:
    # Local/dev: Gmail SMTP with App Password (only works where 587/465 is open)
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")

    if env_bool("EMAIL_USE_SSL", False):
        EMAIL_PORT = env_int("EMAIL_PORT", 465)
        EMAIL_USE_SSL = True
        EMAIL_USE_TLS = False
    else:
        EMAIL_PORT = env_int("EMAIL_PORT", 587)
        EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
        EMAIL_USE_SSL = False

    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "juliavictorio16@gmail.com")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # 16-char Gmail App Password

else:
    # Safe default: print emails to console (never crash checkout)
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Common email settings
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "juliavictorio16@gmail.com")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_TIMEOUT = env_int("EMAIL_TIMEOUT", 20)

# Addresses your views expect
CONTACT_RECEIVER_EMAIL = os.getenv("CONTACT_RECEIVER_EMAIL", "juliavictorio16@gmail.com")
ADMIN_ORDER_EMAIL = os.getenv("ADMIN_ORDER_EMAIL", "juliavictorio16@gmail.com")

# Legacy variable kept if some code still references it
CONTACT_TO = os.environ.get('CONTACT_TO', 'juliavictorio16@gmail.com')

LOGIN_URL = "dashboard_login"
