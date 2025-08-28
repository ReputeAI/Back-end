FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
COPY reputeai ./reputeai
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . --prefix=/install

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY reputeai ./reputeai
CMD ["uvicorn", "reputeai.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
