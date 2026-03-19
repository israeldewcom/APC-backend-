from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FaceProfile, DeviceFingerprint
from .serializers import FaceProfileSerializer, DeviceFingerprintSerializer
import face_recognition
import pickle
from django.core.exceptions import ValidationError

class FaceProfileView(generics.RetrieveUpdateAPIView):
    queryset = FaceProfile.objects.all()
    serializer_class = FaceProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, created = FaceProfile.objects.get_or_create(user=self.request.user)
        return obj

    def perform_update(self, serializer):
        image_data = self.request.data.get('image')
        if image_data:
            import base64
            from io import BytesIO
            from PIL import Image
            import numpy as np
            image_bytes = base64.b64decode(image_data)
            img = Image.open(BytesIO(image_bytes))
            img = img.convert('RGB')
            face_encodings = face_recognition.face_encodings(np.array(img))
            if not face_encodings:
                raise ValidationError("No face detected")
            encoding = face_encodings[0]
            encrypted = pickle.dumps(encoding)
            serializer.save(encoding=encrypted)
        else:
            serializer.save()

class DeviceFingerprintView(generics.ListCreateAPIView):
    serializer_class = DeviceFingerprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeviceFingerprint.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
