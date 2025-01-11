import logging
import os
from typing import ParamSpec

from celery import Celery
from celery.app.log import Logging
from celery.signals import after_setup_logger

from django.conf import settings

P = ParamSpec("P")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "store.settings")

app = Celery("store")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@after_setup_logger.connect()
def on_after_setup_logger(logger: Logging, *args: P.args, **kwargs: P.kwargs) -> None:  # noqa: ARG001
    formatter = logger.handlers[0].formatter
    file_handler = logging.FileHandler("celery.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
