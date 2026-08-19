FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN addgroup --system --gid 10001 appgroup \
    && adduser \
        --system \
        --uid 10001 \
        --ingroup appgroup \
        --no-create-home \
        appuser

COPY backend/requirements-runtime.txt /tmp/requirements-runtime.txt

RUN pip install --no-cache-dir \
    -r /tmp/requirements-runtime.txt

COPY backend/alembic.ini ./alembic.ini
COPY backend/alembic ./alembic
COPY backend/app ./app

RUN chown -R appuser:appgroup /app

USER 10001:10001

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]