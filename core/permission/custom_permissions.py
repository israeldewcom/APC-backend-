from rest_framework.permissions import BasePermission
from apps.close_friends.models import CloseFriend
# NEW imports
from apps.multi_tenant.models import OrganizationMembership
from apps.rbac.models import RolePermission

class IsVerifiedMember(BasePermission):
    message = 'Account verification required. Please complete NIN and fingerprint verification.'
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_verified or request.user.nin_verified

class IsOwnerOrModerator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.has_role_permission('moderate_content'):
            return True
        if hasattr(obj, 'author'):
            return obj.author == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsGroupAdmin(BasePermission):
    message = 'Group admin permission required.'
    def has_permission(self, request, view):
        group_id = view.kwargs.get('group_id') or request.data.get('group_id')
        if not group_id:
            return False
        from apps.groups.models import GroupMember
        return GroupMember.objects.filter(
            group_id=group_id,
            user=request.user,
            role__in=['owner', 'super_admin', 'admin'],
            status='active'
        ).exists()

class IsPlatformAdmin(BasePermission):
    message = 'Platform administrator access required.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class IsSuperAdmin(BasePermission):
    message = 'Super administrator access required.'
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'super_admin')

# NEW permissions for stories, live, etc.
class CanViewStory(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.close_friends.models import CloseFriend
        if obj.user == request.user:
            return True
        if obj.privacy == 'public':
            return True
        if obj.privacy == 'followers':
            return request.user.following.filter(following=obj.user).exists()
        if obj.privacy == 'close_friends':
            return CloseFriend.objects.filter(user=obj.user, friend=request.user).exists()
        return False

# NEW PERMISSIONS FOR UPGRADE

class IsOrganizationMember(BasePermission):
    """Check if user is a member of the current organization (from request.org)"""
    message = 'You must be a member of this organization.'
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        org = getattr(request, 'organization', None)
        if not org:
            return False
        return OrganizationMembership.objects.filter(
            organization=org,
            user=request.user,
            is_active=True
        ).exists()

class HasOrganizationRole(BasePermission):
    """
    Checks if user has a specific role in the current organization.
    Role name is expected in view.required_roles (list).
    """
    message = 'Insufficient organization role.'
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        org = getattr(request, 'organization', None)
        if not org:
            return False
        required_roles = getattr(view, 'required_roles', [])
        if not required_roles:
            return True
        try:
            membership = OrganizationMembership.objects.get(
                organization=org,
                user=request.user,
                is_active=True
            )
            return membership.role.name in required_roles
        except OrganizationMembership.DoesNotExist:
            return False

class HasPermission(BasePermission):
    """
    Check if user has a specific permission (by codename) in the current context.
    Permission string can be passed in view.permission_required.
    """
    message = 'Permission denied.'
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        perm_codename = getattr(view, 'permission_required', None)
        if not perm_codename:
            return True
        return request.user.has_perm(perm_codename)

    def has_object_permission(self, request, view, obj):
        perm_codename = getattr(view, 'permission_required', None)
        if not perm_codename:
            return True
        return request.user.has_perm(perm_codename, obj)
