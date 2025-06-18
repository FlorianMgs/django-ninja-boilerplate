from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import logging

logger = logging.getLogger("db")
channel_layer = get_channel_layer()


@shared_task(bind=True, queue="io_queue")
def streaming_task(self):
    """
    Test task that streams progress to WebSocket clients
    Uses async_to_sync to properly handle channel layer communication
    """
    logger.info(f"Starting streaming task: {self.request.id}")

    try:
        for i in range(10):
            # Simulate work
            time.sleep(2)

            progress = (i + 1) * 10
            message = f"Processing step {i + 1}/10 - {progress}% complete"

            # Send progress update to WebSocket group
            async_to_sync(channel_layer.group_send)(
                "test_group",
                {
                    "type": "task_update",
                    "message": message,
                    "task_id": self.request.id,
                    "progress": progress,
                    "step": i + 1,
                    "total_steps": 10,
                },
            )

            logger.info(f"Task {self.request.id}: {message}")

        # Send completion message
        async_to_sync(channel_layer.group_send)(
            "test_group",
            {
                "type": "task_update",
                "message": "Task completed successfully!",
                "task_id": self.request.id,
                "progress": 100,
                "status": "completed",
            },
        )

        logger.info(f"Completed streaming task: {self.request.id}")
        return {"status": "completed", "result": "Task finished successfully"}

    except Exception as exc:
        logger.exception(f"Task {self.request.id} failed: {exc}")

        # Send error message to WebSocket
        async_to_sync(channel_layer.group_send)(
            "test_group",
            {
                "type": "task_update",
                "message": f"Task failed: {str(exc)}",
                "task_id": self.request.id,
                "status": "failed",
                "error": str(exc),
            },
        )

        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(queue="cpu_queue")
def periodic_test_task():
    """
    Periodic task that sends updates to WebSocket clients
    Runs every 5 minutes via Celery Beat
    """
    import datetime

    logger.info("Running periodic test task")

    current_time = datetime.datetime.now().isoformat()

    try:
        async_to_sync(channel_layer.group_send)(
            "test_group",
            {
                "type": "task_update",
                "message": "Periodic task executed successfully",
                "timestamp": current_time,
                "task_type": "periodic",
                "status": "success",
            },
        )

        logger.info(f"Periodic task completed at {current_time}")
        return {"status": "success", "timestamp": current_time}

    except Exception as exc:
        logger.exception(f"Periodic task failed: {exc}")
        raise
