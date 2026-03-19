from celery import shared_task
from core.utils.moderation import ModerationService
from apps.moderation.models import ContentReport

@shared_task(queue='ai')
def ai_moderate_content(content_type, object_id):
    # Placeholder for AI moderation
    pass

@shared_task(queue='ai')
def generate_smart_reply(conversation_id, message_id):
    # Placeholder for smart reply generation
    pass
