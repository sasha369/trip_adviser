from rest_framework.views import exception_handler as drf_handler
from rest_framework.exceptions import APIException


class DomainError(APIException):
    status_code = 422


def exception_handler(exc, context):
    response = drf_handler(exc, context)
    if response is not None:
        response.data = {"code": ..., "detail": ..., "fields": response.data}
    return response
