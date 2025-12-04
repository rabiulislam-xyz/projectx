import errno
import logging.handlers
import os
import time

import uuid

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

try:
    from asgiref.local import Local
except ImportError:
    from threading import local as Local

local = Local()

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER_SETTING = 'LOG_REQUEST_ID_HEADER'
LOG_REQUESTS_SETTING = 'LOG_REQUESTS'
LOG_REQUESTS_NO_SETTING = 'NO_REQUEST_ID'
LOG_USER_ATTRIBUTE_SETTING = 'LOG_USER_ATTRIBUTE'
DEFAULT_NO_REQUEST_ID = "none"  # Used if no request ID is available
REQUEST_ID_RESPONSE_HEADER_SETTING = 'REQUEST_ID_RESPONSE_HEADER'
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER_SETTING = 'GENERATE_REQUEST_ID_IF_NOT_IN_HEADER'


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

# its duplicate function from utils.misc
# adding here to avoid circular import
def _convert_to_bool_(param, nullable=False):
    if param in ["true", "True", True, "yes", "Yes"]:
        return True

    if nullable:
        if param in ["null", "None", None]:
            return None

    return False


class RotatingFileHandlerMakeDir(logging.handlers.RotatingFileHandler):
    """
    Handler for logging to a set of files, which switches from one file
    to the next when the current file reaches a certain size. Creates
    the folder mentioned if it does not exist.
    """
    def __init__(self,
                 filename,
                 mode='a',
                 maxBytes=0,
                 backupCount=0,
                 encoding=None,
                 delay=False):
        dir_name = os.path.dirname(filename)
        if dir_name:
            mkdir_p(dir_name)
        super().__init__(filename, mode, maxBytes, backupCount, encoding,
                         delay)


class RequestIDMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_request(self, request):
        request_id = self._get_request_id(request)
        local.request_id = request_id
        request.id = request_id
        request.start_time = time.time()

    def get_log_message(self, request, response, request_response_duration):
        user = getattr(request, 'user', None)
        user_attribute = getattr(settings, LOG_USER_ATTRIBUTE_SETTING, False)
        if user_attribute:
            user_id = getattr(user, user_attribute, None)
        else:
            user_id = getattr(user, 'pk', None) or getattr(user, 'id', None)
        message = ' == method=%s path=%s status=%s duration=%s' % (request.method, request.path, response.status_code, request_response_duration)
        if user_id:
            message += ' user=' + str(user_id)
        if request.GET:
            message += ' query=' + str(request.GET.urlencode())
        return message

    def process_response(self, request, response):
        if getattr(settings, REQUEST_ID_RESPONSE_HEADER_SETTING, False) and getattr(request, 'id', None):
            response[getattr(settings, REQUEST_ID_RESPONSE_HEADER_SETTING)] = request.id

        if not getattr(settings, LOG_REQUESTS_SETTING, False):
            return response

        # Don't log favicon
        if 'favicon' in request.path:
            return response

        # don't log admin paths
        if 'api/superAmdin' in request.path:
            return response

        # don't log ping api
        if 'api/ping' in request.path:
            return response

        try:
            request_response_duration = time.time() - request.start_time
        except Exception:
            request_response_duration = -1

        logger.info(self.get_log_message(request, response, request_response_duration))

        try:
            del local.request_id
        except AttributeError:
            pass

        response["X-request-response-duration"] = request_response_duration
        return response

    def _get_request_id(self, request):
        request_id_header = getattr(settings, REQUEST_ID_HEADER_SETTING, None)
        generate_request_if_not_in_header = getattr(settings, GENERATE_REQUEST_ID_IF_NOT_IN_HEADER_SETTING, False)

        if request_id_header:
            # fallback to NO_REQUEST_ID if settings asked to use the
            # header request_id but none provided
            default_request_id = getattr(settings, LOG_REQUESTS_NO_SETTING, DEFAULT_NO_REQUEST_ID)

            # unless the setting GENERATE_REQUEST_ID_IF_NOT_IN_HEADER
            # was set, in which case generate an id as normal if it wasn't
            # passed in via the header
            if generate_request_if_not_in_header:
                default_request_id = self._generate_id()

            return request.META.get(request_id_header, default_request_id)

        return self._generate_id()

    def _generate_id(self):
        return uuid.uuid4().hex


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        default_request_id = getattr(settings, LOG_REQUESTS_NO_SETTING, DEFAULT_NO_REQUEST_ID)
        record.request_id = getattr(local, 'request_id', default_request_id)
        return True


class IgnoreMissingFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = "N/A"
        return super().format(record)
