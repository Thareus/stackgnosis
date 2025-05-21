from django.conf import settings
from django.core import mail
from django.utils.log import AdminEmailHandler
from django.views.generic import FormView


def request_is_ajax(request):
    """Checks if a request was made through Ajax and returns as a boolean"""
    try:
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    except:
        return None

def isoweekday_to_name(isoweekday):
    names = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }
    return names[isoweekday]

def month_to_name(month, abbreviate=False):
    names = {
        1:"January",
        2:"Febraury",
        3:"March",
        4:"April",
        5:"May",
        6:"June",
        7:"July",
        8:"August",
        9:"September",
        10:"October",
        11:"November",
        12:"December",
    }
    if abbreviate:
        return names[month][:3]
    else:
        return names[month]

def datetime_in_utcisoformat(dt):
    """
    Return a datetime object in ISO 8601 format as UTC e.g. '2011-06-28T00:00:00Z'.
    """
    import datetime
    if not dt:
        return ""
    elif type(dt) == str:
        dt = datetime.datetime.fromisoformat(dt)
    # Convert datetime to UTC, remove microseconds, remove timezone, convert to string
    TZ = datetime.timezone(settings.TIME_ZONE)
    try:
        datetime_in_utc = TZ.localize(dt.replace(microsecond=0))
    except ValueError:
        datetime_in_utc = dt
    datetime_in_utc = datetime_in_utc.astimezone('utc')
    datetime_in_utc = datetime_in_utc.replace(tzinfo=None).isoformat() + 'Z'
    return datetime_in_utc

def get_parent_class_names(cls):
    try:
        return [parent_class.__name__ for parent_class in cls.__mro__]
    except AttributeError:
        return [parent_class.__name__ for parent_class in cls.__bases__]

def get_approximate_table_count(model):
    from django.db import connection
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT reltuples FROM pg_class WHERE relname = '{table_name}'")
        approximate_count = cursor.fetchone()[0]
    return approximate_count

def read_static_file_from_gcs(filename):
    """
    A function for reading a static file from a Google Storage Bucket.
    The filepath includes the filename.
    :param filename:
    """
    import os
    from google.cloud import storage
    storage_client = storage.Client(project=os.environ.get('GS_PROJECT_ID'), credentials=settings.GS_CREDENTIALS)
    bucket = storage_client.get_bucket(os.environ.get('GS_BUCKET_NAME'))
    blob = bucket.blob(filename)
    content = blob.download_as_text()
    return content

class StackgnosisAdminEmailHandler(AdminEmailHandler):
    """
    Overrides some methods in the AdminEmailHandler class so that they work.
    """
    def connection(self):
        connection = mail.get_connection(
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD
        )
        return connection

    def send_mail(self, subject, message, *args, **kwargs):
        kwargs['fail_silently'] = False
        mail.mail_admins(subject, message, connection=self.connection(), **kwargs)

