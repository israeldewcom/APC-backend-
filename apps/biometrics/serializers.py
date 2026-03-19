from rest_framework import serializers
from .models import FaceProfile, DeviceFingerprint

class FaceProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class DeviceFingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceFingerprint
        fields = '__all__'
        read_only_fields = ['id', 'last_seen']
