import uuid
from django.db import models
from django.conf import settings

class KeyExchange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='key_exchanges')
    public_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Key for {self.user} at {self.created_at}"
