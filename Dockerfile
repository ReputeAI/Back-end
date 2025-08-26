FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir fastapi uvicorn SQLAlchemy>=2.0 alembic psycopg[binary] pydantic>=2.0 redis celery[redis] httpx python-jose[cryptography] passlib[argon2] python-multipart structlog slowapi tenacity

COPY reputeai ./reputeai

CMD ["uvicorn", "reputeai.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
