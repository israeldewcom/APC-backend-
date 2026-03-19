from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('roles', views.RoleViewSet)
router.register('assignments', views.RoleAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
