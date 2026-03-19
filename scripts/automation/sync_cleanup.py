#!/usr/bin/env python
"""
Clean up old sync queue entries.
Run daily via cron.
"""
import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apc_project.settings')
django.setup()

from apps.sync.models import SyncQueue

def run():
    cutoff = timezone.now() - timedelta(days=7)
    deleted, _ = SyncQueue.objects.filter(created_at__lt=cutoff).delete()
    print(f"Deleted {deleted} old sync queue items")

if __name__ == '__main__':
    run()
