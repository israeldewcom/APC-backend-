from rest_framework import generics, permissions
from .models import SyncQueue
from .serializers import SyncQueueSerializer

class SyncQueueView(generics.ListCreateAPIView):
    serializer_class = SyncQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SyncQueue.objects.filter(user=self.request.user, synced_at__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
