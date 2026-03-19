from django.urls import path
from . import views

urlpatterns = [
    path('queue/', views.SyncQueueView.as_view(), name='sync-queue'),
]
