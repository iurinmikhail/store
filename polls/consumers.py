import json
from typing import Any

from asgiref.sync import async_to_sync
from celery.result import AsyncResult
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


def get_task_info(task_id: str) -> dict[str, Any]:
    """Возвращацет информацию."""
    task = AsyncResult(task_id)
    state = task.state

    if state == "FAILURE":
        error = str(task.result)
        response = {
            "state": state,
            "error": error,
        }
    else:
        response = {
            "state": state,
        }
    return response


def notify_channel_layer(task_id: str) -> None:
    """Вызывается в задаче Celery, так как Celery все еще не поддерживает
    `asyncio`, поэтому используется async_to_sync, чтобы сделать её синхронной

    https://channels.readthedocs.io/en/stable/topics/channel_layers.html#using-outside-of-consumers
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        task_id,
        {"type": "update_task_status", "data": get_task_info(task_id)},
    )


class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]

        await self.channel_layer.group_add(
            self.task_id,
            self.channel_name,
        )

        await self.accept()

        await self.send(text_data=json.dumps(get_task_info(self.task_id)))

    async def disconnect(self, close_code: Any) -> None:  # noqa: ARG002, ANN401
        await self.channel_layer.group_discard(
            self.task_id,
            self.channel_name,
        )

    async def update_task_status(self, event: dict[str, str]) -> None:
        data = event["data"]

        await self.send(text_data=json.dumps(data))
