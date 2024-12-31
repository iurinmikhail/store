import random
from typing import ParamSpec

import requests
from celery import Task, shared_task
from celery.signals import task_postrun
from celery.utils.log import get_task_logger

from polls.consumers import notify_channel_layer

logger = get_task_logger(__name__)

P = ParamSpec("P")


class RandomError(Exception): ...


@task_postrun.connect
def task_postrun_handler(task_id: str, *args: P.args, **kwargs: P.kwargs) -> None:  # noqa: ARG001
    notify_channel_layer(task_id)


def simulate_error(error_message: str = "") -> None:
    """Проверяет условие и вызывает ошибку, если оно выполняется."""
    if not random.choice([0, 1]):  # noqa: S311
        raise RandomError(error_message)


@shared_task()
def sample_task(email: str) -> None:
    from polls.views import api_call

    api_call(email)


@shared_task(bind=True)
def task_process_notification(self: Task) -> None:
    try:
        simulate_error()

        # Блокирующий зарпос
        requests.post("https://httpbin.org/delay/5", timeout=(60, 60))
    except RandomError as e:
        logger.exception("RandomError raised, it would be retry after 5 seconds")
        self.retry(exc=e, countdown=5)


@shared_task(name="task_clear_session")
def task_clear_session() -> None:
    """Задача очистки истекших сессий.
    https://docs.djangoproject.com/en/5.1/ref/django-admin/#clearsessions
    """
    from django.core.management import call_command

    call_command("clearsessions")
