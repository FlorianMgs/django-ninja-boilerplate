# Django Ninja API Boilerplate

A production-ready Django Ninja API boilerplate with Celery, Channels, and Docker support.

## Features

- **Django 5** with Django Ninja for fast API development
- **API Key Authentication** using Django 5's GeneratedField
- **Real-time WebSockets** with Django Channels
- **Background Tasks** with Celery (Redis broker)
- **Containerized** with Docker and Docker Compose
- **Admin Interface** with Django Jazzmin
- **Database Logging** with django-db-logger
- **Task Monitoring** with Celery Flower
- **Hot Reload** for development

## Architecture

```
api-boilerplate/
├── core/                    # Django project
│   ├── apps/               # Custom apps
│   │   ├── auth/          # Authentication with API keys
│   │   └── example/       # Example app with all features
│   ├── core/              # Django settings
│   ├── static/            # Static files
│   └── manage.py
├── docker/                # Docker configuration
└── pyproject.toml         # Poetry dependencies
```

## Quick Start

### 1. Environment Setup

Create a `.env` file in the project root with the following content:

```bash
# Django Core
DJANGO_SETTINGS_MODULE=core.settings.development
DJANGO_SECRET_KEY=development-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgresql://django:secure_postgres_password_123@postgres:5432/postgres
POSTGRES_PASSWORD=secure_postgres_password_123

# Redis & Celery
REDIS_URL=redis://:redis_secure_password_456@redis:6379/0
REDIS_PASSWORD=redis_secure_password_456
CELERY_BROKER_URL=redis://:redis_secure_password_456@redis:6379/0
CELERY_RESULT_BACKEND=redis://:redis_secure_password_456@redis:6379/0

# Celery Workers Configuration
CELERY_IO_WORKERS=1000  # Gevent workers for I/O tasks
CELERY_CPU_WORKERS=4    # Process workers for CPU tasks

# Logging
DJANGO_DB_LOGGER_ADMIN_LIST_PER_PAGE=50
DJANGO_DB_LOGGER_ENABLE_FORMATTER=True

# Security
SECURE_SSL_REDIRECT=False
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

### 2. Start Services

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up --build

# Or run in background
docker-compose -f docker/docker-compose.yml up -d --build
```

### 3. Access Services

- **API Documentation**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin/
- **Flower (Task Monitor)**: http://localhost:5555 (requires authentication)
- **WebSocket**: ws://localhost:8000/ws/test/

### 4. Get Admin API Key

Check the Docker logs to get the admin user's API key:

```bash
docker-compose -f docker/docker-compose.yml logs web | grep "API key"
```

## API Usage

### Authentication

All API endpoints require an API key in the header:

```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:8000/api/example/test
```

### Example Endpoints

```bash
# Get user profile
GET /api/auth/me

# Test endpoint
GET /api/example/test

# Trigger streaming task
POST /api/example/trigger-task

# Get user info
GET /api/example/user-info

# Health check (no auth required)
GET /api/health
```

### WebSocket Usage

Connect to the WebSocket and authenticate:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/test/');

ws.onopen = function() {
    // Authenticate with API key
    ws.send(JSON.stringify({
        type: 'auth',
        api_key: 'your_api_key_here'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send ping
ws.send(JSON.stringify({
    type: 'ping',
    timestamp: Date.now()
}));
```

## Development

### Local Development (without Docker)

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Set up environment variables** in your shell or `.env` file

3. **Run services**:
   ```bash
   # Terminal 1: Django server
   cd core
   poetry run python manage.py runserver

   # Terminal 2: Celery worker
   cd core
   poetry run celery -A core worker -Q io_queue,cpu_queue --loglevel=info

   # Terminal 3: Celery beat
   cd core
   poetry run celery -A core beat --scheduler django_celery_beat.schedulers:DatabaseScheduler

   # Terminal 4: Flower
   cd core
   poetry run celery -A core flower
   ```

### Database Migrations

```bash
# Create migrations
docker-compose -f docker/docker-compose.yml exec web python manage.py makemigrations

# Apply migrations
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate
```

### Create Admin User

```bash
docker-compose -f docker/docker-compose.yml exec web python manage.py createsuperuser
```

## Project Structure

### Apps

- **`apps/auth/`**: User authentication with API key generation
- **`apps/example/`**: Example app demonstrating all features

### Key Files

- **`core/settings/`**: Environment-based settings (dev/prod)
- **`core/celery.py`**: Celery configuration with queue routing
- **`core/asgi.py`**: ASGI application for HTTP + WebSocket
- **`core/urls.py`**: Main URL configuration with API routes

### Docker Services

- **`web`**: Django + Channels ASGI server
- **`celery-worker`**: Background task processing
- **`celery-beat`**: Periodic task scheduling
- **`celery-flower`**: Task monitoring dashboard
- **`postgres`**: PostgreSQL database
- **`redis`**: Redis (broker + channel layer)

## API Key Management

### Generate New API Key

```python
# In Django shell
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='admin')
user.regenerate_api_key()
print(f"New API key: {user.api_key}")
```

### Disable API Key

```python
user.is_api_key_active = False
user.save()
```

## Background Tasks

### Task Queues

- **`io_queue`**: I/O bound tasks (API calls, file operations)
- **`cpu_queue`**: CPU intensive tasks (data processing)

### Example Task

```python
from apps.example.tasks import streaming_task

# Trigger task
task = streaming_task.delay()
print(f"Task ID: {task.id}")
```

## Monitoring

### Celery Flower

Access Flower at http://localhost:5555 to monitor:
- Active tasks
- Worker status
- Queue lengths
- Task history

Flower requires authentication using the credentials defined in your `.env` file (`ADMIN_USERNAME` and `ADMIN_PASSWORD`).

### Database Logs

View application logs in the Django admin at `/admin/django_db_logger/statuslog/`

## Production Deployment

1. **Update environment variables** for production
2. **Use production settings**:
   ```bash
   DJANGO_SETTINGS_MODULE=core.settings.production
   ```
3. **Enable HTTPS** and update security settings
4. **Scale services** as needed:
   ```bash
   docker-compose up --scale celery-worker=4
   ```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 5432, 6379, 5555 are available
2. **Permission errors**: Check Docker user permissions
3. **Database connection**: Verify PostgreSQL is running and accessible
4. **Redis connection**: Check Redis authentication and connectivity

### Logs

```bash
# View all logs
docker-compose -f docker/docker-compose.yml logs

# View specific service logs
docker-compose -f docker/docker-compose.yml logs web
docker-compose -f docker/docker-compose.yml logs celery-worker
```

## License

This project is open source and available under the MIT License. 