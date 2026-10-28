import json
import logging
import time
import uuid
from contextvars import ContextVar

request_id_var = ContextVar("request_id", default=None)
logger = logging.getLogger("api.request")


class ObservabilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request_id_var.set(request_id)
        request.request_id = request_id

        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = round((time.monotonic() - start) * 1000)

        actor = getattr(request, "user", None)
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "actor_id": str(getattr(actor, "id", "") or ""),
                    "route": request.path,
                    "method": request.method,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                },
                ensure_ascii=False,
            )
        )

        response["X-Request-ID"] = request_id
        return response
