import http

from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_handler


class DomainError(APIException):
    status_code = 422

    def __init__(self, code: str, detail: str, fields: dict | None = None):
        self.domain_code = code
        self.fields = fields or {}
        super().__init__(detail=detail)


class AuthError(APIException):
    """Ошибка аутентификации на auth-эндпоинтах (неверные креды и т.п.)."""

    def __init__(
        self,
        code: str,
        detail: str,
        status_code: int = http.HTTPStatus.UNAUTHORIZED,
        fields: dict | None = None,
    ):
        self.domain_code = code
        self.status_code = int(status_code)
        self.fields = fields or {}
        super().__init__(detail=detail)


def exception_handler(exc, context):
    response = drf_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, (DomainError, AuthError)):
        data = {
            "code": exc.domain_code,
            "detail": str(exc.detail),
            "fields": exc.fields,
        }
    elif response.status_code == 400 and isinstance(response.data, dict):
        data = {
            "code": "validation_error",
            "detail": "Ошибка валидации",
            "fields": response.data,
        }
    else:
        detail = (
            response.data.get("detail")
            if isinstance(response.data, dict)
            else response.data
        )
        data = {
            "code": getattr(exc, "default_code", "error"),
            "detail": str(detail),
            "fields": {},
        }
    response.data = data
    return response
