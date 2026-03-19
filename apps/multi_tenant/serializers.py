from rest_framework import serializers
from .models import Organization, OrganizationMembership
from apps.users.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrganizationMembership
        fields = '__all__'
