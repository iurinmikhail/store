from django.urls import path

from polls.views import subscribe, subscribe_ws, task_status, transaction_celery, webhook_test, webhook_test_async

urlpatterns = [
    path("form/", subscribe, name="form"),
    path("task_status/", task_status, name="task_status"),
    path("webhook_test/", webhook_test, name="webhook_test"),
    path("webhook_test_async/", webhook_test_async, name="webhook_test_async"),
    path("form_ws/", subscribe_ws, name="form_ws"),
    path("transaction_celery/", transaction_celery, name="transaction_celery"),
]
