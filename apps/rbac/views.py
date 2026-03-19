from rest_framework import viewsets, permissions
from .models import Role, RoleAssignment
from .serializers import RoleSerializer, RoleAssignmentSerializer
from core.permissions.custom_permissions import IsPlatformAdmin

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsPlatformAdmin]

class RoleAssignmentViewSet(viewsets.ModelViewSet):
    queryset = RoleAssignment.objects.all()
    serializer_class = RoleAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPlatformAdmin]
