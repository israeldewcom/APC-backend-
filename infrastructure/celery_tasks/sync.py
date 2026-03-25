from celery import shared_task
from django.utils import timezone
from apps.sync.models import SyncQueue

@shared_task(queue='sync')
def process_sync_queue(user_id, device_id):
    pending = SyncQueue.objects.filter(user_id=user_id, device_id=device_id, synced_at__isnull=True)
    for item in pending:
        # In production, you would dynamically apply the change using Django's ORM
        # e.g., if item.model_name == 'Post' and item.action == 'create':
        #     Post.objects.create(**item.data)
        item.synced_at = timezone.now()
        item.save()
    return f"Processed {pending.count()} items"
