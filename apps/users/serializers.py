from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'full_name', 'phone', 'bio',
            'avatar', 'cover_photo', 'date_of_birth', 'gender',
            'is_verified', 'nin_verified', 'fingerprint_registered',
            'is_active', 'is_admin', 'role',
            'date_joined', 'last_login', 'updated_at',
            'following_count', 'followers_count',
            'privacy_settings',
            # NEW
            'public_key', 'face_encoding', 'sync_token',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'updated_at']

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers_count(self, obj):
        return obj.followers.count()
