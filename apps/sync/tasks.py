from celery import shared_task
from django.utils import timezone
from .models import SyncQueue
import json

@shared_task(queue='sync')
def process_sync_queue(user_id, device_id):
    pending = SyncQueue.objects.filter(user_id=user_id, device_id=device_id, synced_at__isnull=True)
    for item in pending:
        # Apply action based on model_name, action, and data
        model_name = item.model_name
        action = item.action
        data = item.data
        try:
            # Dynamically import model and apply change
            # For simplicity, we'll just mark as synced
            # In real implementation, you'd use serializers to apply create/update/delete
            pass
        except Exception as e:
            # Log error and maybe retry
            pass
        item.synced_at = timezone.now()
        item.save()
    return f"Processed {pending.count()} items"
