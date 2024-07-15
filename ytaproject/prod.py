import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name, default=None):
    """Get the environment variable or return exception if no default is set."""
    try:
        return os.getenv(var_name, default)
    except KeyError:
        if default is None:
            error_msg = f"Set the {var_name} environment variable"
            raise ImproperlyConfigured(error_msg)
        return default

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY', 'django-insecure-vnjh%ecew(+5*#+w74=jb55t_chknj3-)#9u!v08^(7@=ofug#')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = get_env_variable('DJANGO_DEBUG', 'False').lower() == 'true'
DEBUG=True

ALLOWED_HOSTS = get_env_variable('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'ytauser',
    'yta_app',
    # 'schema_graph',

]
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "https://*",  # Add your trusted origins here
    "http://*",  # Add your trusted origins here
]


# Allow credentials (cookies, authorization headers) to be sent with CORS requests
CORS_ALLOW_CREDENTIALS = True
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.TokenAuthentication',
#     ),
# }
# CSRF_COOKIE_DOMAIN = "lostdiscover.asia.squirrelvision.ai"
# Allow credentials (cookies, authorization headers) to be sent with CORS requests
CORS_ALLOW_CREDENTIALS = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')


CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    'DELETE',
    'PUT',
    "OPTIONS",
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

CSRF_TRUSTED_ORIGINS=['https://be.yta.squirrelvision.ai/']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ytaproject.urls'
AUTH_USER_MODEL = "ytauser.CustomUser"


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ytaproject.wsgi.application'

# Database

DATABASES = {
            'default': {
                'ENGINE': os.environ.get('DJANGO_DATABASE_ENGINE'),  #'django.db.backends.postgresql_psycopg2',
                'NAME': os.environ.get('DJANGO_DATABASE_NAME'), #'sqvision_smartdb',
                'USER': os.environ.get('DJANGO_DATABASE_USER'), #'sqvisionuser',
                'PASSWORD': os.environ.get('DJANGO_DATABASE_PASSWORD'), #'SqVizionBLR@2k24',
                'HOST': os.environ.get('DJANGO_DATABASE_HOST'), #'localhost',
                'PORT': os.environ.get('DJANGO_DATABASE_PORT'), #'5478',
                'OPTIONS': {
                'options': '-c search_path='+os.environ.get('DJANGO_DATABASE_SCHEMA'), #
            }
            }
        }

# Password validation
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
LANGUAGE_CODE = get_env_variable('LANGUAGE_CODE', 'en-us')
TIME_ZONE = get_env_variable('TIME_ZONE', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
MEDIA_URL = '/media/'  # URL for serving media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Absolute filesystem path to the directory that will hold user-uploaded files

# print(CONFIG_ROOT) 
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Define STATIC_ROOT for collecting static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATIC_URL = 'static/'

# Assuming DEBUG is defined earlier in your settings.py
# if not DEBUG:
#     # Production settings
#     STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# else:
#     # Development settings
#     STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Email settings (example using SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_variable('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = get_env_variable('EMAIL_PORT', '587')
EMAIL_USE_TLS = get_env_variable('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# MSG91_AUTH_KEY = os.getenv('MSG91_AUTH_KEY')
# MSG91_SENDER_ID = os.getenv('MSG91_SENDER_ID')

MSG91_AUTH_KEY = os.getenv('MSG91_AUTH_KEY')
MSG91_SENDER_ID = os.getenv('MSG91_SENDER_ID')
MSG91_TEMPLATE_ID = os.getenv('MSG91_TEMPLATE_ID')
OTP_SENDER_DN =  os.getenv('OTP_SENDER')