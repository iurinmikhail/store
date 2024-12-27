import random

import requests
from celery.result import AsyncResult

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from polls.forms import YourForm
from polls.tasks import sample_task


def api_call(email: str) -> None:  # noqa: ARG001
    # Используется для теста возникновения ошибки
    if random.choice([0, 1]):  # noqa: S311
        error_message = "random processing error"
        raise Exception(error_message)  # noqa: TRY002

    # Симулятор вызова блокирующего запроса
    requests.post("https://httpbin.org/delay/5", timeout=5)


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
