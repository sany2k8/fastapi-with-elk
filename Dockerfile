FROM python:3.12-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Install uv by copying the static binary from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install dependencies first (better layer caching — this layer only rebuilds
# when pyproject.toml or uv.lock change, not on every code edit)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the application code
COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]