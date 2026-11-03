# syntax=docker/dockerfile:1

FROM python:$3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Некорневой пользователь; media/static должны быть ему доступны
RUN adduser --disabled-password --gecos "" --no-create-home appuser \
    && mkdir -p /app/media /app/static \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
ENTRYPOINT [ "./entrypoint.sh" ]
CMD ["gunicorn", "backend.wsgi", "--bind=0.0.0.0:8000", "--workers=2", "--timeout=60"]
