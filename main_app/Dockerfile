# syntax=docker/dockerfile:1

FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG REQUIREMENTS_FILE=dev.txt

COPY requirements/ requirements/
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && pip install --no-cache-dir -r requirements/${REQUIREMENTS_FILE} \
    # Удаляем gcc после сборки пакетов, чтобы уменьшить образ, но оставляем libpq-dev
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

WORKDIR /app/main_app

USER root
RUN chmod +x ./entrypoint.sh

# Некорневой пользователь; media/static должны быть ему доступны
RUN adduser --disabled-password --gecos "" --no-create-home appuser \
    && mkdir -p /app/media /app/static \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
ENTRYPOINT [ "./entrypoint.sh" ]
CMD ["gunicorn", "backend.wsgi", "--bind=0.0.0.0:8000", "--workers=2", "--timeout=60"]
