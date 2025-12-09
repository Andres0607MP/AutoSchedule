from rest_framework import serializers
from .models import Service, Ticket

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id','name','description']

class TicketSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id','code','service','service_name','user','user_username','created_at','status']
        read_only_fields = ['code','created_at','user','user_username']

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['service']

    def validate(self, attrs):
        user = self.context['request'].user
        service = attrs['service']
        active = Ticket.objects.filter(user=user, service=service, status='active').exists()
        if active:
            raise serializers.ValidationError("Ya tienes un ticket activo para este servicio")
        return attrs

    def create(self, validated_data):
        import uuid
        user = self.context['request'].user
        service = validated_data['service']
        code = f"{service.name[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
        ticket = Ticket.objects.create(service=service, user=user, code=code)
        return ticket
