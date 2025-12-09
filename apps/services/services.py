from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id", "name", "description", "estimated_time",
            "category", "created_at"
        ]

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["name", "description", "estimated_time", "category"]
