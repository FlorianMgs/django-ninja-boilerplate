from ninja import Router
from authentication.authentication import api_key_auth
from .tasks import streaming_task
from .schemas import TestResponseSchema, TaskResponseSchema
import logging

logger = logging.getLogger("db")
router = Router(tags=["Example"], auth=api_key_auth)


@router.get("/test", response=TestResponseSchema)
def test_endpoint(request):
    """Test endpoint that returns user info"""
    from datetime import datetime

    logger.info(f"Test endpoint accessed by user: {request.auth.username}")

    return TestResponseSchema(
        message="Test endpoint successful",
        user=request.auth.username,
        timestamp=datetime.now().isoformat(),
    )


@router.post("/trigger-task", response=TaskResponseSchema)
def trigger_streaming_task(request):
    """Trigger the streaming task"""
    logger.info(f"Streaming task triggered by user: {request.auth.username}")

    task = streaming_task.delay()

    return TaskResponseSchema(
        message="Streaming task started",
        task_id=task.id,
    )
