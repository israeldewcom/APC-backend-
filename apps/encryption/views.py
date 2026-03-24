from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import KeyExchange
from .serializers import KeyExchangeSerializer
from core.utils.e2ee import encrypt_message, decrypt_message, generate_key_pair

class KeyExchangeListCreateView(generics.ListCreateAPIView):
    queryset = KeyExchange.objects.all()
    serializer_class = KeyExchangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EncryptMessageView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        recipient_id = request.data.get('recipient_id')
        plaintext = request.data.get('message')
        if not recipient_id or not plaintext:
            return Response({'error': 'recipient_id and message required'}, status=400)
        try:
            recipient_key = KeyExchange.objects.filter(user_id=recipient_id, used=False).latest('created_at')
        except KeyExchange.DoesNotExist:
            return Response({'error': 'No public key for recipient'}, status=400)
        encrypted = encrypt_message(plaintext, recipient_key.public_key)
        return Response({'encrypted': encrypted})

class DecryptMessageView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ciphertext = request.data.get('ciphertext')
        if not ciphertext:
            return Response({'error': 'ciphertext required'}, status=400)
        # In real scenario, fetch user's private key (encrypted) and decrypt
        # For demo, we just return a placeholder
        return Response({'decrypted': 'Message would be decrypted client-side'})
