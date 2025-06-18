from ninja import Schema


class TaskResponseSchema(Schema):
    message: str
    task_id: str


class TestResponseSchema(Schema):
    message: str
    user: str
    timestamp: str
