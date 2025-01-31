import logging
import random
import time
from functools import partial
from string import ascii_lowercase

import requests
from celery.result import AsyncResult

from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from polls.forms import YourForm
from polls.tasks import sample_task, simulate_error, task_process_notification, task_send_welcome_email

logger = logging.getLogger(__name__)


def random_username() -> str:
    return "".join([random.choice(ascii_lowercase) for i in range(5)])  # noqa: S311


def api_call(email: str) -> None:  # noqa: ARG001
    simulate_error("random processing error")

    # Блокирующий процесс
    requests.post("https://httpbin.org/delay/5", timeout=(60, 60))


def subscribe(request: HttpRequest) -> JsonResponse | HttpResponse:
    if request.method == "POST":
        form = YourForm(request.POST)
        if form.is_valid():
            task = sample_task.delay(form.cleaned_data["email"])
            return JsonResponse(
                {
                    "task_id": task.task_id,
                },
            )

    form = YourForm()
    return render(request, "form.html", {"form": form})


def task_status(request: HttpRequest) -> JsonResponse | None:
    task_id = request.GET.get("task_id")

    if task_id:
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
        return JsonResponse(response)
    return None


@csrf_exempt
def webhook_test(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    simulate_error()

    # Блокирующий процесс
    requests.post("https://httpbin.org/delay/5", timeout=(60, 60))
    return HttpResponse("pong")


@csrf_exempt
def webhook_test_async(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    """Асинхронно обрабатывает вебхуки."""
    task = task_process_notification.delay()
    logger.info(task.id)
    return HttpResponse("pong")


def subscribe_ws(request: HttpRequest) -> JsonResponse | HttpResponse:
    """Использует вебсокеты для получения уведомления Celery,
    вместо использования опросов ajax
    """
    if request.method == "POST":
        form = YourForm(request.POST)
        if form.is_valid():
            task = sample_task.delay(form.cleaned_data["email"])
            return JsonResponse(
                {
                    "task_id": task.task_id,
                },
            )

    form = YourForm()
    return render(request, "form_ws.html", {"form": form})


@transaction.atomic
def transaction_celery(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    username = random_username()
    user = User.objects.create_user(username, "email@email.org", "password")
    transaction.on_commit(partial(task_send_welcome_email.delay, user.pk))
    time.sleep(1)
    return HttpResponse("test")
