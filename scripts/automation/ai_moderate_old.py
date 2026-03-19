#!/usr/bin/env python
"""
Re‑moderate old posts using AI.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apc_project.settings')
django.setup()

from apps.posts.models import Post
from infrastructure.celery_tasks.ai_moderation import moderate_content

def run():
    posts = Post.objects.filter(created_at__gte=timezone.now() - timedelta(days=30))
    for post in posts:
        moderate_content.delay('post', post.id)
    print(f"Queued {posts.count()} posts for moderation")

if __name__ == '__main__':
    from django.utils import timezone
    from datetime import timedelta
    run()
