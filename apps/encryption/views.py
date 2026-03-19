from rest_framework import generics, permissions
from .models import KeyExchange
from .serializers import KeyExchangeSerializer

class KeyExchangeListCreateView(generics.ListCreateAPIView):
    queryset = KeyExchange.objects.all()
    serializer_class = KeyExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class KeyExchangeDetailView(generics.RetrieveAPIView):
    queryset = KeyExchange.objects.all()
    serializer_class = KeyExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]
