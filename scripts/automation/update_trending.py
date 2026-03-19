#!/usr/bin/env python
"""
Manually trigger trending hashtags update.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apc_project.settings')
django.setup()

from infrastructure.celery_tasks.recommendations import update_trending_hashtags

if __name__ == '__main__':
    update_trending_hashtags.delay()
    print("Trending update task queued")
