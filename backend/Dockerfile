# ---------------------------------------------------------------------------
# StandOut Backend — production image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ---------------------------------------------------------------------------
# Dependencies layer (cached unless pyproject.toml changes)
# ---------------------------------------------------------------------------
FROM base AS deps

COPY pyproject.toml ./

# Install the project in editable mode so the app package is importable.
# --no-cache-dir keeps the image small.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Application layer
# ---------------------------------------------------------------------------
FROM deps AS runtime

COPY . .

EXPOSE 8000

# Run with uvicorn.  In production, pair this with a reverse-proxy (e.g.
# nginx / Traefik / Cloud Run front-end) that handles TLS termination.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
