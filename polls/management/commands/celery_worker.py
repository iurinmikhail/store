import logging
import shlex
import subprocess
import sys
from typing import ParamSpec

from django.core.management.base import BaseCommand
from django.utils import autoreload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

P = ParamSpec("P")


def restart_celery() -> None:
    celery_worker_cmd = "celery -A store worker"
    cmd = ["pkill", "-f", celery_worker_cmd]
    if sys.platform == "win32":
        cmd = ["taskkill", "/f", "/t", "/im", "celery.exe"]
    try:
        subprocess.run(cmd, check=True)  # noqa: S603
        subprocess.run(shlex.split(f"{celery_worker_cmd} --loglevel=info"), check=True)  # noqa: S603
    except subprocess.CalledProcessError:
        logger.exception("Error occurred while restarting Celery:")


class Command(BaseCommand):
    def handle(self, *args: P.args, **options: P.kwargs) -> None:  # noqa: ARG002
        autoreload.run_with_reloader(restart_celery)
