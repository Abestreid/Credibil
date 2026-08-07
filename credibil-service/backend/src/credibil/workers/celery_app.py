from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from credibil.config import get_settings

settings = get_settings()

celery_app = Celery(
    "credibil",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=86400,
    broker_transport_options={
        "visibility_timeout": 3600,
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.5,
        "interval_max": 3,
    },
)

celery_app.conf.beat_schedule = {
    "moldova-bulk-sync-daily": {
        "task": "credibil.workers.tasks.sync_moldova_bulk",
        "schedule": crontab(hour=2, minute=0),  # 02:00 UTC daily
        "kwargs": {"sync_type": "incremental"},
    },
    "court-hearings-sync-daily": {
        "task": "credibil.workers.tasks.sync_court_hearings",
        "schedule": crontab(hour=3, minute=0),  # 03:00 UTC daily
        "kwargs": {"court_slug": None},
    },
    "tenders-sync-daily": {
        "task": "credibil.workers.tasks.sync_tenders_recent",
        "schedule": crontab(hour=4, minute=0),  # 04:00 UTC daily
        "kwargs": {"limit": 50},
    },
    "enforcement-full-crawl-daily": {
        "task": "credibil.workers.tasks.sync_enforcement_full",
        "schedule": crontab(hour=6, minute=0),  # 06:00 UTC daily
        "kwargs": {"max_pages": 60},
    },
    "monitoring-checks-daily": {
        "task": "credibil.workers.tasks.run_monitoring_checks",
        # 08:00 UTC — after the bulk/court/enforcement syncs have refreshed data.
        "schedule": crontab(hour=8, minute=0),
    },
    "moldac-accreditations-sync-daily": {
        "task": "credibil.workers.tasks.sync_moldova_accreditations",
        "schedule": crontab(hour=5, minute=0),  # 05:00 UTC daily
        "kwargs": {"category": None},
    },
    "search-reindex-all-daily": {
        "task": "credibil.workers.tasks.search_reindex_all",
        "schedule": crontab(hour=1, minute=0),  # 01:00 UTC daily
    },
    "sanctions-sweep-all-companies-weekly": {
        "task": "credibil.workers.tasks.sync_sanctions_all_companies",
        "schedule": crontab(hour=7, minute=0, day_of_week=0),  # Sunday 07:00 UTC
    },
}

celery_app.autodiscover_tasks(["credibil.workers"])
