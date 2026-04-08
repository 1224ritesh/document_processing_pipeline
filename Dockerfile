FROM python:3.12-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

# Install all deps into .venv, no uv cache kept
RUN uv sync --frozen --no-install-project --no-cache

COPY app/ ./app/

RUN uv sync --frozen --no-cache


FROM python:3.12-slim

WORKDIR /app

# Copy only the venv and app — no uv, no build cache, no pip
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
