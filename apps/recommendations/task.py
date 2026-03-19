from celery import shared_task
from django.core.cache import cache
from apps.hashtags.models import Hashtag
from django.db.models import Count

@shared_task(queue='recommendations')
def update_trending_hashtags():
    trending = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]
    cache.set('trending_hashtags', [{'name': h.name, 'count': h.post_count} for h in trending], 3600)
    return "Trending updated"
