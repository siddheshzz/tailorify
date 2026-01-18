"""
Celery configuration for asynchronous task processing.
Handles email notifications and bulk campaigns.
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "tailorify",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.campaign_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,
    task_reject_on_worker_lost=True,
    
    # Worker configuration
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    worker_disable_rate_limits=False,
    
    # Result backend
    result_expires=settings.CELERY_RESULT_EXPIRES,
    result_persistent=True,
    
    # Optimization
    task_compression="gzip",
    result_compression="gzip",
    
    # Error handling
    task_send_sent_event=True,
    worker_send_task_events=True,
)

# Task routing - separate queues for different task types
celery_app.conf.task_routes = {
    "app.tasks.email_tasks.send_order_confirmation_email": {"queue": "emails"},
    "app.tasks.email_tasks.send_template_email": {"queue": "emails"},
    "app.tasks.campaign_tasks.send_bulk_campaign": {"queue": "campaigns"},
    "app.tasks.campaign_tasks.send_single_campaign_email": {"queue": "campaigns"},
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Example: Daily cleanup task at 2 AM UTC
    "cleanup-old-tasks": {
        "task": "app.tasks.maintenance_tasks.cleanup_old_results",
        "schedule": crontab(hour=2, minute=0),
    },
    # Example: Weekly report every Monday at 9 AM UTC
    # "weekly-report": {
    #     "task": "app.tasks.report_tasks.generate_weekly_report",
    #     "schedule": crontab(hour=9, minute=0, day_of_week=1),
    # },
}

# Task priority settings (0-9, higher number = higher priority)
celery_app.conf.task_default_priority = 5
celery_app.conf.task_inherit_parent_priority = True

# Rate limits (to prevent overwhelming external services)
celery_app.conf.task_annotations = {
    "app.tasks.email_tasks.send_order_confirmation_email": {"rate_limit": "100/m"},
    "app.tasks.email_tasks.send_template_email": {"rate_limit": "100/m"},
    "app.tasks.campaign_tasks.send_single_campaign_email": {"rate_limit": "50/m"},
}