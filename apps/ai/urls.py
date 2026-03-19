from django.urls import path
from . import views

urlpatterns = [
    path('smart-reply/', views.SmartReplyView.as_view(), name='smart-reply'),
]
