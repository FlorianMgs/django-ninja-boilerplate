import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from apps.common.logger_utils import async_log_info, async_log_exception


class ExampleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.authenticated = False
        self.user = None
        await self.accept()

        # Send authentication challenge
        await self.send(
            text_data=json.dumps(
                {
                    "type": "auth_required",
                    "message": "Please authenticate with your API key",
                    "format": {"type": "auth", "api_key": "your_api_key_here"},
                }
            )
        )

        # Set timeout for authentication
        import asyncio

        asyncio.create_task(self.auth_timeout())

    async def auth_timeout(self):
        """Close connection if not authenticated within 30 seconds"""
        import asyncio

        await asyncio.sleep(30)
        if not self.authenticated:
            await self.send(
                text_data=json.dumps(
                    {"type": "auth_timeout", "message": "Authentication timeout"}
                )
            )
            await self.close(code=4008)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get("type") == "auth" and not self.authenticated:
                api_key = data.get("api_key")
                if not api_key:
                    await self.send(
                        text_data=json.dumps(
                            {"type": "auth_error", "message": "API key is required"}
                        )
                    )
                    return

                user = await self.authenticate_user(api_key)

                if user:
                    self.authenticated = True
                    self.user = user
                    await self.channel_layer.group_add("test_group", self.channel_name)

                    await self.send(
                        text_data=json.dumps(
                            {
                                "type": "auth_success",
                                "message": f"Welcome {user.username}! You are now connected.",
                                "user": {
                                    "username": user.username,
                                    "is_staff": user.is_staff,
                                },
                            }
                        )
                    )

                    # Use async-safe logging
                    await async_log_info(f"WebSocket authenticated: {user.username}")
                else:
                    await self.send(
                        text_data=json.dumps(
                            {"type": "auth_error", "message": "Invalid API key"}
                        )
                    )
                    await self.close(code=4001)

            elif self.authenticated:
                # Handle authenticated messages
                await self.handle_authenticated_message(data)
            else:
                await self.send(
                    text_data=json.dumps(
                        {"type": "error", "message": "Please authenticate first"}
                    )
                )

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid JSON format"}
                )
            )
        except Exception as e:
            # Use async-safe logging
            await async_log_exception(f"WebSocket error: {e}")
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Internal server error"}
                )
            )
            await self.close(code=4000)

    async def handle_authenticated_message(self, data):
        """Handle messages from authenticated users"""
        message_type = data.get("type")

        if message_type == "ping":
            await self.send(
                text_data=json.dumps(
                    {"type": "pong", "timestamp": data.get("timestamp")}
                )
            )
        else:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    }
                )
            )

    async def disconnect(self, close_code):
        if self.authenticated:
            await self.channel_layer.group_discard("test_group", self.channel_name)
            # Use async-safe logging
            username = self.user.username if self.user else "Unknown"
            await async_log_info(f"WebSocket disconnected: {username}")

    async def task_update(self, event):
        """Receive task updates from Celery"""
        if self.authenticated:
            await self.send(
                text_data=json.dumps({"type": "task_update", "data": event})
            )

    @database_sync_to_async
    def authenticate_user(self, api_key):
        try:
            User = get_user_model()
            return User.objects.get(api_key=api_key, is_api_key_active=True)
        except User.DoesNotExist:
            return None
