from django.urls import path
from . import views

urlpatterns = [
    path('face/', views.FaceProfileView.as_view(), name='face-profile'),
    path('devices/', views.DeviceFingerprintView.as_view(), name='device-list'),
]
