import random
from typing import ClassVar, ParamSpec

import requests
from celery import Task, shared_task
from celery.signals import task_postrun
from celery.utils.log import get_task_logger

from polls.consumers import notify_channel_layer

logger = get_task_logger(__name__)

P = ParamSpec("P")


class RandomError(Exception): ...


class BaseTaskWithRetry(Task):
    autoretry_for: ClassVar[tuple[type, ...]] = (RandomError,)
    retry_kwargs: ClassVar[dict[str, int]] = {"max_retries": 5}
    retry_backoff: ClassVar[bool] = True


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


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_process_notification(self: Task) -> None:  # noqa: ARG001
    simulate_error()

    # Блокирующий зарпос
    requests.post("https://httpbin.org/delay/5", timeout=(60, 60))


@shared_task(name="task_clear_session")
def task_clear_session() -> None:
    """Задача очистки истекших сессий.
    https://docs.djangoproject.com/en/5.1/ref/django-admin/#clearsessions
    """
    from django.core.management import call_command

    call_command("clearsessions")


@shared_task(name="default:dynamic_example_one")
def dynamic_example_one() -> None:
    logger.info("Example One")


@shared_task(name="low_priority:dynamic_example_two")
def dynamic_example_two() -> None:
    logger.info("Example Two")


@shared_task(name="high_priority:dynamic_example_three")
def dynamic_example_three() -> None:
    logger.info("Example Three")


@shared_task(name="divide")
def divide(x: int, y: int) -> float:
    from time import sleep

    sleep(5)
    return x / y
