from rest_framework.views import exception_handler
from core.utils.mail import send_error_500_email
import traceback

def scp_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response is None:
        # Notify 500 error
        send_error_500_email(str(exc), context['request'].path, traceback.format_exc())
    return response