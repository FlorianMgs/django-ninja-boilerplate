FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Install poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./
RUN poetry install --only=main --no-interaction --no-ansi

# Copy application
COPY --chown=django:django ./core .
COPY --chown=django:django ./docker/entrypoint.sh ./entrypoint.sh

# Make entrypoint executable
RUN chmod +x ./entrypoint.sh

# Create necessary directories with proper permissions
RUN mkdir -p static staticfiles media logs && \
    chown -R django:django static staticfiles media logs && \
    chmod -R 755 static staticfiles media logs

# Don't switch to django user yet - let entrypoint handle it

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f -H "X-API-Key: health-check" http://localhost:8000/health/ || exit 1

# Default command
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"] 