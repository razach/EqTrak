# Use Python 3.11 slim image as base
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=EqTrak.settings \
    DEBUG=True

# Set work directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY EqTrak/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create static directory
RUN mkdir -p /workspace/staticfiles

# Expose port
EXPOSE 8000

# Set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Command to run on container start
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "EqTrak/manage.py", "runserver", "0.0.0.0:8000"]