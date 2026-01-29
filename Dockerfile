# Multi-stage build for optimized image size
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================
# Production stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 efys && \
    mkdir -p /app/uploads /app/logs && \
    chown -R efys:efys /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/efys/.local

# Copy application code
COPY --chown=efys:efys . .

# Set Python path
ENV PATH=/home/efys/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Switch to non-root user
USER efys

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
