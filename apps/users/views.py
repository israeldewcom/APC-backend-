from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User
from .serializers import UserSerializer
from core.permissions.custom_permissions import IsOwnerOrModerator

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]

    @action(detail=True, methods=['post'])
    def set_public_key(self, request, pk=None):
        user = self.get_object()
        public_key = request.data.get('public_key')
        encrypted_private_key = request.data.get('encrypted_private_key')
        if not public_key or not encrypted_private_key:
            return Response({'error': 'Both keys required'}, status=400)
        user.public_key = public_key
        user.encrypted_private_key = encrypted_private_key
        user.save()
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'])
    def sync_token(self, request, pk=None):
        user = self.get_object()
        user.sync_token = request.data.get('sync_token', '')
        user.save()
        return Response({'status': 'ok'})
