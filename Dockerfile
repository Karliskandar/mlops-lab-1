# -------------------------
# Stage 1: Builder
# -------------------------
FROM python:3.13 AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv
# --no-install-project is used because the source code
# has intentionally not been copied yet.
RUN uv sync --frozen --no-dev --no-install-project


# -------------------------
# Stage 2: Runtime
# -------------------------
FROM python:3.13-slim AS runtime

WORKDIR /app

# Copy only the prepared virtual environment
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ ./src/

# Use executables from the copied virtual environment
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["uvicorn","src.food11.serve:app","--host","0.0.0.0","--port","8000"]