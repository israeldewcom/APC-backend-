import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert not user.is_admin

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass'
        )
        assert user.is_admin
        assert user.is_superuser
