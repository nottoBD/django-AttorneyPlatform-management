"""
Django settings for fExtra project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path
import django_heroku
from django.utils.translation import gettext_lazy as _
from django.contrib.messages import constants as messages
import environ

# Run python manage.py collectstatic if you are moving to production. This command collects static files from your apps and any other directories specified in STATICFILES_DIRS into the directory specified by STATIC_ROOT.
# During development, Django's development server automatically serves static files found in your apps' static directories and those specified in STATICFILES_DIRS, provided you have DEBUG = True in your settings.py.


BASE_DIR = Path(__file__).resolve().parent.parent


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

env = environ.Env()
environ.Env.read_env(env_file=str(BASE_DIR / ".env"))
SECRET_KEY = env('DJANGO_SECRET_KEY')

# print(list(env.ENVIRON.keys())) # !

# SECURITY WARNING: no DEBUG in production. Key stored locally .env
# SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['fextra/herokuapp.com']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'crispy_forms',
    'crispy_bootstrap5',
    'guardian',
]

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Default Django auth
    'guardian.backends.ObjectPermissionBackend', # Guardian permission
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

LANGUAGES = [
    ('fr', _('French')),
    ('en', _('English')),
    ('nl-BE', _('Dutch')),
    ('de', _('German')),
]

LANGUAGE_CODE = 'fr'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

ROOT_URLCONF = 'fExtra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'fExtra.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'da7j83t1pptldd',
        'USER': 'humxhvqvueqfru',
        'PASSWORD': '6f43f22aff941c48c4518973b380cc9ea185578b2e0ea468a4db8e76a9da5ed3',
        'HOST': 'ec2-34-251-233-253.eu-west-1.compute.amazonaws.com',
        'PORT': '5432'
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

TIME_ZONE = 'Europe/Brussels'
USE_I18N = True
USE_TZ = True

#TODO: toast & notification
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = "/static/"
django_heroku.settings(locals())


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'accounts', 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login'

ANONYMOUS_USER_NAME = None