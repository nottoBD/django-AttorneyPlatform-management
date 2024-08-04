import os
from pathlib import Path
from environ import environ
from django.utils.translation import gettext_lazy as _

DEBUG = False

ALLOWED_HOSTS = ['38.180.87.128', 'jurinet.net', 'neok-budget.eu', 'app.neok-budget.eu', 'neok-budget.be']

BASE_DIR = Path(__file__).resolve().parent.parent

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

env = environ.Env()

environ.Env.read_env(env_file=str(BASE_DIR / ".env"))

SECRET_KEY = env('SECRET_KEY')

EMAIL_BACKEND = env('EMAIL_BACKEND')

EMAIL_HOST = env('EMAIL_HOST')

EMAIL_HOST_USER = env('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

EMAIL_PORT = env('EMAIL_PORT', cast=int)

EMAIL_USE_TLS = env('EMAIL_USE_TLS', cast=bool)

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

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
    'payments.apps.PaymentsConfig',
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
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
    ('nl-BE', _('Flemish')),
    ('de', _('German')),
]

LANGUAGE_CODE = 'fr'
  
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

ROOT_URLCONF = 'neok.urls'

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

WSGI_APPLICATION = 'neok.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT')
    }
}
  
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

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
  
LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/accounts/login'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ANONYMOUS_USER_NAME = None

COOKIEBANNER = {
    "title": _("Cookie settings"),
    "header_text": _("We are using a few essential cookies on this website."),
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
                {
                    "pattern": "django_language",
                    "description": _("Stores the language preference of the user."),
                },
            ],
        },
    ],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
