# Multi-stage Dockerfile for Blockchain CARF Framework
# Optimized for security and minimal image size

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN useradd -m -u 1000 carf && \
    mkdir -p /app /data /vault && \
    chown -R carf:carf /app /data /vault

WORKDIR /app

# Install dependencies stage
FROM base as dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM base as final

# Copy installed dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=carf:carf src/ /app/src/
COPY --chown=carf:carf examples/ /app/examples/

# Set secure permissions
RUN chmod 755 /app/src && \
    chmod 700 /vault && \
    chmod 755 /data

# Switch to non-root user
USER carf

# Expose volume mount points
VOLUME ["/data", "/vault"]

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["python", "-m", "src"]

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import src; print('OK')" || exit 1
