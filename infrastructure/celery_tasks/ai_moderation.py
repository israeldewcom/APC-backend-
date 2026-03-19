from celery import shared_task
from core.utils.moderation import ModerationService
from apps.moderation.models import ContentReport

@shared_task(queue='ai')
def moderate_content(content_type, object_id):
    if content_type == 'post':
        from apps.posts.models import Post
        post = Post.objects.get(id=object_id)
        service = ModerationService()
        result = service.check_text(post.content)
        if not result['safe']:
            post.is_blocked = True
            post.save()
            ContentReport.objects.create(
                content_type='post',
                object_id=post.id,
                reason='AI moderation',
                details=result
            )
    return "Moderated"
