"""
APScheduler configuration for background jobs.
Started from app/apps.py AppConfig.ready() — runs once on server start.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

_scheduler = None


def sync_membership_payments():
    """Hourly job: sync Google Sheets → MembershipPayment table."""
    from webapp.sheets_sync import sync_all
    try:
        result = sync_all()
        if result['success']:
            logger.info(
                f"Sheets sync OK — added:{result['total_added']} "
                f"updated:{result['total_updated']} errors:{result['total_errors']}"
            )
        else:
            logger.warning(f"Sheets sync failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"Scheduler job error: {e}")


def start():
    """Start the background scheduler. Safe to call multiple times."""
    global _scheduler
    if _scheduler is not None:
        return

    try:
        _scheduler = BackgroundScheduler(timezone='Asia/Dhaka')
        _scheduler.add_jobstore(DjangoJobStore(), 'default')

        _scheduler.add_job(
            sync_membership_payments,
            trigger=IntervalTrigger(hours=1),
            id='sync_membership_payments',
            name='Sync Google Sheets → MembershipPayment',
            replace_existing=True,
        )

        _scheduler.start()
        logger.info("Background scheduler started. Sheets sync runs every hour.")
    except Exception as e:
        logger.error(f"Scheduler failed to start: {e}")
        _scheduler = None
