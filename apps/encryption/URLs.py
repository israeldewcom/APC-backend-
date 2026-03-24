from django.urls import path
from . import views

urlpatterns = [
    path('keys/', views.KeyExchangeListCreateView.as_view(), name='key-list'),
    path('keys/<uuid:pk>/', views.KeyExchangeDetailView.as_view(), name='key-detail'),
    path('encrypt/', views.EncryptMessageView.as_view(), name='encrypt'),
    path('decrypt/', views.DecryptMessageView.as_view(), name='decrypt'),
]
