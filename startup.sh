#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Running database migrations..."
# Assuming you're using Django's manage.py for migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist already
# This script uses environment variables to avoid hardcoding credentials
if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]] && [[ -n "$DJANGO_SUPERUSER_EMAIL" ]] && [[ -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
    echo "Creating superuser if it doesn't exist..."
    python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL || echo "Superuser already exists"
else
    echo "Skipping superuser creation because environment variables are not set"
fi

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8001}
