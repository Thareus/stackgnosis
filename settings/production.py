import io
import environ
from google.cloud import secretmanager_v1

from .base import *

env = environ.Env()

env.read_env(os.path.join("/app", "envs", ".prod"))

SETTINGS_NAME=env('DJANGO_ENV')
DEBUG=False
# Set Template Debug
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
DEFAULT_HTTP_PROTOCOL="https"

SECRET_KEY=env("SECRET_KEY")

project_id = env("GOOGLE_CLOUD_PROJECT")
settings_name = env("GOOGLE_SECRET_NAME")
name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
client = secretmanager_v1.SecretManagerServiceClient()
payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
env.read_env(io.StringIO(payload))

STATIC_URL = env('STATIC_URL')
DEFAULT_FILE_STORAGE = env('DEFAULT_FILE_STORAGE')
STATICFILES_STORAGE = env('DEFAULT_FILE_STORAGE')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Collected by `collectstatic`
GS_BUCKET_NAME = env('GS_BUCKET_NAME')
GS_MEDIA_LOCATION = env('GS_MEDIA_LOCATION')

MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_MEDIA_LOCATION}/'

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("POSTGRESQL_DB_NAME"),
        'USER': env("POSTGRESQL_DB_USER"),
        'PASSWORD': env("POSTGRESQL_DB_PASSWORD"),
        'HOST': env("POSTGRESQL_DB_HOST"),
        'PORT': env("POSTGRESQL_DB_PORT")
    },
}

SECURE_SSL_REDIRECT = True
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
PREPEND_WWW = False

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Options: 'mandatory', 'optional', 'none'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('DJANGO_APP_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True