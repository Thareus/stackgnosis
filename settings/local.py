import environ
from .base import *

env = environ.Env()

env.read_env(str(BASE_DIR / "envs"/ ".local"))

SETTINGS_NAME=env('DJANGO_ENV')
DEBUG=True
# Set Template Debug
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
DEFAULT_HTTP_PROTOCOL="http"

SECRET_KEY=env("SECRET_KEY")

OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_MODEL_NAME = env("OPENAI_API_MODEL")

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'http://localhost:8000/', ]
BASE_URL = 'http://127.0.0.1:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("POSTGRESQL_DB_NAME"),
        'USER': env("POSTGRESQL_DB_USER"),
        'PASSWORD': env("POSTGRESQL_DB_PASSWORD"),
        'HOST': env("POSTGRESQL_DB_HOST"),
        'PORT': env("POSTGRESQL_DB_PORT")
    }
}

STATIC_URL = env('STATIC_URL')
DEFAULT_FILE_STORAGE = env('DEFAULT_FILE_STORAGE')
STATIC_ROOT = 'staticfiles'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Options: 'mandatory', 'optional', 'none'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

CONTACT_EMAIL = tuple(env('CONTACT_EMAIL').split(','))

ADMINS = [
    tuple(env('ADMINS').split(',')),
]

SESSION_COOKIE_SECURE = False