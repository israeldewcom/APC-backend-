from celery import shared_task
from django.utils import timezone
from .models import SyncQueue

@shared_task(queue='sync')
def process_sync_queue(user_id, device_id):
    pending = SyncQueue.objects.filter(user_id=user_id, device_id=device_id, synced_at__isnull=True)
    for item in pending:
        # Apply action
        pass
    pending.update(synced_at=timezone.now())
    return f"Processed {pending.count()} items"
