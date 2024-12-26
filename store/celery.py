import os

from celery import Celery

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "store.settings")

app = Celery("store")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def divide(x: int, y: int) -> float:
    import time

    time.sleep(5)
    return x / y
