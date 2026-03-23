from datetime import datetime, timezone

import requests

from app.extensions import db
from app.models import Vendor, VendorSyncQueue
from app.utils.logger import get_logger

logger = get_logger("services.vendor_sync")


def transform_payload(entity_type, payload):
    """Apply vendor-specific transformations."""
    return payload


def process_vendor_sync_queue():
    """Process pending outbound sync items."""
    items = (
        VendorSyncQueue.query.filter_by(sync_status="pending")
        .order_by(VendorSyncQueue.created_at)
        .all()
    )
    for item in items:
        vendor = db.session.get(Vendor, item.vendor_id)
        if not vendor:
            logger.warning("Vendor %s not found for sync item %s", item.vendor_id, item.id)
            continue
        try:
            transformed = transform_payload(item.entity_type, item.payload)
            resp = requests.post(
                f"{vendor.vendor_api_config['endpoint']}/sync",
                json=transformed,
                headers={"Authorization": (f"Bearer {vendor.vendor_api_config['apiKey']}")},
                timeout=30,
            )
            if resp.status_code == 200:
                item.sync_status = "synced"
                item.processed_at = datetime.now(timezone.utc)
                item.transformed_payload = transformed
                logger.info("Sync item %s synced to vendor %s", item.id, item.vendor_id)
            else:
                item.sync_status = "failed"
                item.error_message = f"HTTP {resp.status_code}"
                logger.error("Sync item %s failed: HTTP %s", item.id, resp.status_code)
        except Exception:
            item.sync_status = "failed"
            item.error_message = "Sync request failed"
            logger.exception("Sync item %s raised an exception", item.id)
        item.attempts += 1
        item.last_attempt_at = datetime.now(timezone.utc)
        db.session.commit()
