from rest_framework import viewsets, permissions
from .models import Organization, OrganizationMembership
from .serializers import OrganizationSerializer, OrganizationMembershipSerializer
from core.permissions.custom_permissions import IsPlatformAdmin, HasOrganizationRole

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsPlatformAdmin]

class OrganizationMembershipViewSet(viewsets.ModelViewSet):
    queryset = OrganizationMembership.objects.all()
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAuthenticated, HasOrganizationRole]
    required_roles = ['owner', 'admin']

    def get_queryset(self):
        org_id = self.request.query_params.get('organization')
        if org_id:
            return self.queryset.filter(organization_id=org_id)
        return self.queryset
