import uuid
from django.db import models
from django.conf import settings

class FaceProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='face_profile')
    encoding = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Face profile for {self.user}"

class DeviceFingerprint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    fingerprint = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_trusted = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'fingerprint']

    def __str__(self):
        return f"Device {self.fingerprint} for {self.user}"
