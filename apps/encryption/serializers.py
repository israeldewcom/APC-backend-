from rest_framework import serializers
from .models import KeyExchange

class KeyExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyExchange
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'used']
