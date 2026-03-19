import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)

    # Profile
    bio = models.TextField(blank=True)
    avatar = models.ForeignKey('media.Media', null=True, blank=True, on_delete=models.SET_NULL, related_name='user_avatar')
    cover_photo = models.ForeignKey('media.Media', null=True, blank=True, on_delete=models.SET_NULL, related_name='user_cover')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)

    # Verification & security
    is_verified = models.BooleanField(default=False)
    nin_verified = models.BooleanField(default=False)
    fingerprint_registered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.CharField(max_length=50, default='member')

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    blocked_users = models.ManyToManyField('self', symmetrical=False, related_name='blocked_by', blank=True)

    # Device tracking
    last_device_id = models.CharField(max_length=255, blank=True)
    trusted_devices = models.JSONField(default=list, blank=True)

    # Privacy settings
    privacy_settings = models.JSONField(default=dict, blank=True)

    # NEW FIELDS FOR UPGRADE
    public_key = models.TextField(blank=True)
    encrypted_private_key = models.TextField(blank=True)
    face_encoding = models.BinaryField(null=True, blank=True)
    last_face_capture = models.DateTimeField(null=True, blank=True)
    sync_token = models.CharField(max_length=255, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

    def has_role_permission(self, perm):
        from apps.rbac.models import Role
        role = Role.objects.filter(name=self.role).first()
        if role:
            return role.permissions.filter(codename=perm).exists()
        return False

    def has_perm(self, perm, obj=None):
        if self.has_role_permission(perm):
            return True
        if obj is not None:
            from guardian.shortcuts import get_perms
            return perm in get_perms(self, obj)
        return False
