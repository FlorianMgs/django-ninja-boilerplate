from celery import Celery
from django.conf import settings
import os

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

app = Celery("core")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Configure task routing and execution
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routing
app.conf.task_routes = {
    "apps.example.tasks.streaming_task": {"queue": "io_queue"},
    "apps.example.tasks.periodic_test_task": {"queue": "cpu_queue"},
}

# Queue configuration
app.conf.task_default_queue = "default"
app.conf.task_queues = {
    "io_queue": {
        "routing_key": "io_queue",
    },
    "cpu_queue": {
        "routing_key": "cpu_queue",
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
