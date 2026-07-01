# IT Help Desk ADK Agent — Dockerfile
# Multi-stage build: keeps the final image small.

# ── Builder stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into a dedicated directory so we can copy only them
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Non-root user for security
RUN useradd --no-create-home --shell /bin/false agentuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy agent source
COPY . .

# Cloud Run injects PORT; ADK's built-in server respects it
ENV PORT=8080

# Run as non-root
USER agentuser

# ADK serves the agent via its built-in web server
CMD ["python", "-m", "google.adk.cli", "api_server", "--port", "8080", "--agent", "agent"]
