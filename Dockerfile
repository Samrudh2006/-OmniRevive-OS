# ==============================================================================
# OmniRevive-OS: Production-Grade Multi-Stage Container
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final minimal runtime image
FROM python:3.12-slim AS runner

WORKDIR /app

# Run as non-root user for fintech compliance and security
RUN useradd -m -u 1001 appuser

COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

COPY backend ./backend
COPY frontend ./frontend
COPY benchmarks ./benchmarks
COPY aws ./aws
COPY autonomous_ai_company_os ./autonomous_ai_company_os
COPY deployment ./deployment
COPY docs ./docs
COPY cli.py ./cli.py

# Ensure write permissions for SQLite WAL audit store
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=3)" || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
