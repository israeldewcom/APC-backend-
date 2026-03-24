from rest_framework import generics, permissions
from .models import SyncQueue
from .serializers import SyncQueueSerializer
from .tasks import process_sync_queue

class SyncQueueView(generics.ListCreateAPIView):
    serializer_class = SyncQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SyncQueue.objects.filter(user=self.request.user, synced_at__isnull=True)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        # Trigger async sync processing
        process_sync_queue.delay(instance.user_id, instance.device_id)
