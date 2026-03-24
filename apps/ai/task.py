from celery import shared_task
from core.utils.moderation import ModerationService
from apps.moderation.models import ContentReport

@shared_task(queue='ai')
def ai_moderate_content(content_type, object_id):
    from apps.posts.models import Post
    from apps.comments.models import Comment  # assuming you have a comments app
    if content_type == 'post':
        try:
            post = Post.objects.get(id=object_id)
        except Post.DoesNotExist:
            return
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
    elif content_type == 'comment':
        # similar
        pass
    return "Moderated"

@shared_task(queue='ai')
def generate_smart_reply(conversation_id, message_id):
    # Placeholder – actual implementation uses OpenAI API
    pass
