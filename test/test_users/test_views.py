import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestUserViewSet:
    def test_list_users_authenticated(self, authenticated_client, test_user):
        url = reverse('user-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_users_unauthenticated(self, api_client):
        url = reverse('user-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
