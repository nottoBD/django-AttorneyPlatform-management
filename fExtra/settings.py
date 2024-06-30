import os
from pathlib import Path
from environ import environ
from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(env_file=str(BASE_DIR / ".env"))

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'Payments.apps.PaymentsConfig',
    'crispy_forms',
    'crispy_bootstrap5',
    'guardian',
    'cookiebanner',
]

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

LANGUAGES = [
    ('fr', 'French'),
    ('en', 'English'),
    ('nl-BE', 'Dutch'),
    ('de', 'German'),
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

# Postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dbtest',
        'USER': 'usertest',
        'PASSWORD': 'usertest',
        'PORT': '5432'
    }
}

# Mysql
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'neok',
#         'USER': 'user',
#         'PASSWORD': 'Neok',
#     }
# }

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

TIME_ZONE = 'Europe/Brussels'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/accounts/login'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ANONYMOUS_USER_NAME = None

COOKIEBANNER = {
    "title": _("Cookie settings"),
    "header_text": _("We are using cookies on this website. A few are essential, others are not."),
    "footer_text": _("Please accept our cookies"),
    "footer_links": [
        {"title": _("Imprint"), "href": "/imprint"},
        {"title": _("Privacy"), "href": "/privacy"},
    ],
    "groups": [
        {
            "id": "essential",
            "name": _("Essential"),
            "description": _("Essential cookies allow this page to work."),
            "cookies": [
                {
                    "pattern": "cookiebanner",
                    "description": _("Meta cookie for the cookies that are set."),
                },
                {
                    "pattern": "csrftoken",
                    "description": _("This cookie prevents Cross-Site-Request-Forgery attacks."),
                },
                {
                    "pattern": "sessionid",
                    "description": _("This cookie is necessary to allow logging in, for example."),
                },
            ],
        },
        {
            "id": "analytics",
            "name": _("Analytics"),
            "optional": True,
            "cookies": [
                {
                    "pattern": "_pk_.*",
                    "description": _("Matomo cookie for website analysis."),
                },
            ],
        },
    ],
}