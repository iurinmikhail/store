from django.urls import path

from polls.views import subscribe, task_status, webhook_test

urlpatterns = [
    path("form/", subscribe, name="form"),
    path("task_status/", task_status, name="task_status"),
    path("webhook_test/", webhook_test, name="webhook_test"),
]
