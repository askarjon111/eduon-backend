import logging
from simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # checks if the raised exception is of the type you want to handle
    if isinstance(exc, TokenError):
        # defines custom response data
        err_data = {
            "error": "Token invalid or expired"
        }

        # logs detail data from the exception being handled
        logging.error(f"Original error detail and callstack: {exc}")
        # returns a JsonResponse
        return Response(err_data, status=401)

    # returns response as handled normally by the framework
    return response