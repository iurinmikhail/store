FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y build-essential \
    libpq-dev \
    gettext \
    git \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendImport=false \
    && rm -rf /var/lib/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install uv
RUN uv pip install --system -r /requirements.txt

COPY ./compose/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./compose/local/django/celery/worker/start /start-worker
RUN sed -i 's/\r$//g' /start-worker
RUN chmod +x /start-worker

COPY ./compose/local/django/celery/beat/start /start-beat
RUN sed -i 's/\r$//g' /start-beat
RUN chmod +x /start-beat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
