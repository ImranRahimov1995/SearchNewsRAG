FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

WORKDIR /app

FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

COPY backend/pyproject.toml backend/poetry.lock* ./
RUN poetry install --only main --no-root --no-ansi

COPY rag_module/setup.py rag_module/pyproject.toml /tmp/rag-build/
COPY rag_module/rag_module /tmp/rag-build/rag_module

WORKDIR /tmp/rag-build
RUN /app/.venv/bin/pip install --no-cache-dir .
WORKDIR /app
RUN rm -rf /tmp/rag-build

FROM base AS runtime

ARG PORT=8000
ARG HOST=0.0.0.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PORT=${PORT} \
    HOST=${HOST}

COPY --chown=appuser:appuser backend/src ./src

RUN mkdir -p logs chroma_db && \
    chown -R appuser:appuser logs chroma_db

USER appuser

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health').read()"]

CMD ["/app/.venv/bin/python", "src/main.py"]