"""
Django settings for automotive project.
"""

from pathlib import Path
import os
from django.contrib.messages import constants as messages
import environ
import boto3
from botocore.exceptions import NoCredentialsError
import watchtower
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()

# Read the .env file
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'localflavor',
    'crispy_forms',
    'django_filters',
    'crispy_bootstrap5',
    'main',
    'users',
    'storages',
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

ROOT_URLCONF = 'automotive.urls'

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

WSGI_APPLICATION = 'automotive.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
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

# AWS Programmatic Configuration
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
#AWS_SESSION_TOKEN = env("AWS_SESSION_TOKEN", default=None)
AWS_SNS_TOPIC_ARN = env("AWS_SNS_TOPIC_ARN")

def get_s3_client():
    """
    Returns a boto3 S3 client for programmatic access.
    """
    try:
        session = boto3.session.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            #aws_session_token=AWS_SESSION_TOKEN,
            region_name=AWS_S3_REGION_NAME,
        )
        return session.client('s3')
    except NoCredentialsError:
        raise Exception("AWS Credentials not found. Ensure .env is configured correctly.")

# Static and Media Storage Configuration
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
}

STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/static/'
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"

MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/media/'
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Collectstatic configuration
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # App-level static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directory for collectstatic



# Login settings
LOGIN_REDIRECT_URL = '/home/'
LOGIN_URL = '/login/'

# Messages Settings
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Django Crispy forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# AWS SES Configuration
AWS_SES_REGION = env('AWS_SES_REGION')

# Email Backend
EMAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_HOST = f'email.{AWS_SES_REGION}.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
#DEFAULT_FROM_EMAIL = 'aryannci2024@gmail.com'  
AWS_SES_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')


# AWS CloudWatch Configuration
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_REGION = env("AWS_REGION")
CLOUDWATCH_LOG_GROUP = env("CLOUDWATCH_LOG_GROUP", default="AutoVerseLogs")

# CloudWatch Logging Configuration
if not DEBUG:  
    cloudwatch_handler = watchtower.CloudWatchLogHandler(
        log_group=CLOUDWATCH_LOG_GROUP,
        stream_name="AutoVerseStream",
        boto3_session=boto3.session.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        ),
    )
    LOGGING = DEFAULT_LOGGING.copy()
    LOGGING['handlers']['cloudwatch'] = {
        'level': 'INFO',
        'class': 'watchtower.CloudWatchLogHandler',
        'formatter': 'verbose',
    }
    LOGGING['loggers']['django'] = {
        'handlers': ['console', 'cloudwatch'],
        'level': 'INFO',
        'propagate': False,
    }
    LOGGING['formatters'] = {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    }