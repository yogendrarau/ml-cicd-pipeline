# ---------- Builder: resolve and cache dependencies ----------
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip wheel --wheel-dir=/wheels -r requirements.txt

# ---------- Runtime: minimal image with wheels installed ----------
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install runtime deps from built wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy code (no large local artifacts thanks to .dockerignore)
COPY . .

# Default FastAPI port inside container
EXPOSE 8080

# Optional container-level healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s CMD \
  python -c "import requests; import sys; \
  sys.exit(0 if requests.get('http://127.0.0.1:8080/healthz', timeout=2).status_code==200 else 1)" || exit 1

# Start the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]