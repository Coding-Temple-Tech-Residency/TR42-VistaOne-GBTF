from app.utils.logger import get_logger
from celery_app import celery

logger = get_logger("tasks.vendor_sync")


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_vendor_sync_task(self, vendor_id):
    """Process vendor sync queue as a background task."""
    from app.services.vendor_sync_service import process_vendor_sync_queue

    try:
        process_vendor_sync_queue()
    except Exception as exc:
        logger.exception("Vendor sync failed for %s, retrying", vendor_id)
        raise self.retry(exc=exc)
