import uuid
from django.db import models
from django.contrib.auth.models import Permission as DjangoPermission
from django.conf import settings

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(DjangoPermission, blank=True)
    organization = models.ForeignKey('multi_tenant.Organization', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class RoleAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    organization = models.ForeignKey('multi_tenant.Organization', null=True, blank=True, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'role', 'organization']

    def __str__(self):
        return f"{self.user} - {self.role}"
