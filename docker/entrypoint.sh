#!/bin/bash

set -e

echo "Starting entrypoint script..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "Waiting for $service_name..."
    while ! nc -z "$host" "$port"; do
        echo "$service_name is unavailable - sleeping"
        sleep 1
    done
    echo "$service_name is up - continuing..."
}

# Wait for required services
wait_for_service postgres 5432 "PostgreSQL"
wait_for_service redis 6379 "Redis"

echo "All services are available"

# Create staticfiles directory with proper permissions as root
mkdir -p /app/staticfiles /app/static /app/media /app/logs
chown -R django:django /app/staticfiles /app/static /app/media /app/logs
chmod -R 755 /app/staticfiles /app/static /app/media /app/logs

# Only run migrations and setup on web service
if [ "${1}" = "daphne" ] || [ "${1}" = "python" ]; then
    echo "Running Django setup..."
    
    # Run migrations as django user
    su django -c "python manage.py migrate --noinput"
    
    # Create superuser if it doesn't exist
    su django -c "python manage.py shell << 'EOF'
import os
from django.contrib.auth import get_user_model
User = get_user_model()

# Get admin credentials from environment variables
admin_username = os.getenv('ADMIN_USERNAME', 'admin')
admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(is_superuser=True).exists():
    admin_user = User.objects.create_superuser(admin_username, admin_email, admin_password)
    print(f\"Superuser '{admin_username}' created with API key: {admin_user.api_key}\")
else:
    admin_user = User.objects.filter(is_superuser=True).first()
    print(f\"Superuser '{admin_user.username}' exists with API key: {admin_user.api_key}\")
EOF"
    
    # Collect static files as django user
    su django -c "python manage.py collectstatic --noinput"
    
    echo "Django setup completed"
fi

# Execute the main command as django user
exec su django -c "$*" 