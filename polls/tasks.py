import random

import requests
from celery import Task, shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class RandomError(Exception): ...


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
