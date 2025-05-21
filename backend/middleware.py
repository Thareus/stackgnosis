import logging
import os
import traceback

from django.conf import settings
from django.shortcuts import render

from .utils import StackgnosisAdminEmailHandler

###
logger = logging.getLogger('django')
###

class ExceptionMiddleware(StackgnosisAdminEmailHandler):
    """
    This middleware will catch request errors and process them in several ways,
    before returning a respective error page. These pages may be manually triggered by
    going to the url of their respective status code (e.g. /500/).
    Errors are logged according to the configured logger, and an email is sent to admin
    if DEBUG is set to false.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.template_name = 'error.html'
        self.error_types = {
            '400':'Bad Request',
            '403':'Permission Denied',
            '404':'Page not Found',
            '500':'Server Error'
        }

    def send_exception_email(self, request, message, subject_prefix=''):
        request_path = f" at {request.path_info}" if request else ''
        self.send_mail(
            subject=f"{subject_prefix}{request_path}",
            message=message,
            fail_silently=False,
        )
        return True

    def configure_error_response(self, request, exception_message, status_code=500):
        error_message = "Something went wrong"
        # Return a custom error page
        return render(
            request,
            template_name=self.template_name,
            status=status_code,
            context={
                'error_type': self.error_types[str(status_code)],
                'error_message': error_message,
                'exception_message': exception_message
            }
        )

    def process_exception(self, request, exception):
        """
        Will be called if an exception occurs in the midst of get_response
        """
        url = request.build_absolute_uri()
        try:
            data = getattr(request, request.method).dict()
        except AttributeError:
            # Request data is kept only in GET or POST form.
            # DELETE method has no data either way.
            # PUT/PATCH extend from POST
            data = getattr(request, "POST").dict()
        exception = repr(exception)
        traceback_message = traceback.format_exc()
        message = (
            f"{request.user} triggered the following exception\n"
            f"at {url} with the following data:\n{data}\n\n{exception}\n````\n{traceback_message}````"
        )
        if settings.DEBUG or os.getenv('TEST_DEBUG'): # All tests are run with DEBUG = False
            logger.exception(traceback_message)  # Log to console.
            # self.send_exception_email(request, message, subject_prefix=['EXCEPTION']) # Sometimes turned on in development
            return self.configure_error_response(request, message)
        else:
            self.send_exception_email(request, message, subject_prefix=['EXCEPTION'])
            return self.configure_error_response(request, None)

    def __call__(self, request):
        path = request.path_info.strip('/')
        if path in self.error_types.keys() and request.user.is_staff:  # If manual trigger
            return self.configure_error_response(request, "(Manually Triggered)", path)
        else:
            return self.get_response(request)
