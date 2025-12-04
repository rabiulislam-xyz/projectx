import logging
import traceback

from rest_framework import status
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that standardizes error responses
    across validation, authentication, permission, and server errors.
    """

    # Let DRF generate the default response first
    response = exception_handler(exc, context)

    # If DRF already handled it
    if response is not None:
        detail = None

        # Handle ValidationError with flexible structure
        if isinstance(exc, ValidationError):
            error_detail = exc.detail

            # If error_detail is a dict: pick the first key: value pair
            if isinstance(error_detail, dict):
                field, messages = next(iter(error_detail.items()))
                # Flatten message list or single ErrorDetail
                if isinstance(messages, (list, tuple)):
                    message = messages[0]
                elif isinstance(messages, dict):
                    sub_field, sub_messages = next(iter(messages.items()))
                    message = sub_messages[0] if isinstance(sub_messages, (list, tuple)) else sub_messages
                    field = sub_field
                else:
                    message = messages

                if field != "non_field_errors":
                    detail = f"'{field}' {message}"
                else:
                    detail = str(message)

            elif isinstance(error_detail, list):
                # ValidationError raised directly with list of messages
                detail = error_detail[0]
            elif isinstance(error_detail, ErrorDetail):
                detail = str(error_detail)
            else:
                detail = str(error_detail)

        else:
            # For all other handled exceptions (401, 403, 404, etc.)
            detail = str(exc.detail) if hasattr(exc, 'detail') else str(exc)

        # Normalize the output
        response.data = {
            "success": False,
            "status_code": response.status_code,
            "error": response.status_text,
            "detail": detail,
        }

    else:
        # Unhandled exceptions (500, runtime errors, etc.)
        logger.exception(exc)
        response = Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal Server Error",
                "detail": str(exc),
                "traceback": traceback.format_exc().splitlines()[-5:],  # last few lines for dev
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return response
