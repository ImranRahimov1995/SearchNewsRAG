"""Celery application configuration."""

import os

from celery import Celery
from celery.schedules import crontab

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
database_url = os.getenv(
    "DATABASE_URL",
)

celery_app = Celery(
    "searchnewsrag",
    broker=redis_url,
    backend=database_url.replace(
        "postgresql+psycopg", "db+postgresql+psycopg"
    ),
    include=["tasks.news_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_backend_transport_options={"master_name": "mymaster"},
    result_expires=86400,
    timezone="Asia/Baku",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_extended=True,
    beat_schedule={
        "daily-news-update": {
            "task": "tasks.news_tasks.daily_news_update",
            "schedule": crontab(hour=0, minute=1),
        },
    },
)
