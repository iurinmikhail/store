from django.urls import path

from polls.views import subscribe, task_status

urlpatterns = [
    path("form/", subscribe, name="form"),
    path("task_status/", task_status, name="task_status"),
]
