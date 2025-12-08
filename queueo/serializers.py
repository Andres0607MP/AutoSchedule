from rest_framework import serializers
from .models import Service, Ticket


class ServiceSerializer(serializers.ModelSerializer):
    ticket_count = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'estimated_duration', 'created_at', 'updated_at', 'ticket_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_ticket_count(self, obj):
        return obj.tickets.filter(status='active').count()


class TicketSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    time_in_queue = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'code', 'service', 'service_name', 'user', 'user_email',
            'created_at', 'estimated_time', 'completed_at', 'is_called', 'called_at',
            'status', 'priority', 'position_in_queue', 'time_in_queue'
        ]
        read_only_fields = ['code', 'created_at', 'called_at', 'completed_at', 'position_in_queue', 'time_in_queue']

    def get_time_in_queue(self, obj):
        if obj.called_at:
            delta = obj.called_at - obj.created_at
            return int(delta.total_seconds() / 60)
        return None

    def validate_status(self, value):
        if value not in ['active', 'cancelled', 'completed', 'in_service']:
            raise serializers.ValidationError("Estado inválido")
        return value


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['service', 'priority']

    def create(self, validated_data):
        user = self.context['request'].user
        service = validated_data['service']
        priority = validated_data.get('priority', 'medium')
        
        active_count = Ticket.objects.filter(
            user=user, service=service, status='active'
        ).count()
        
        if active_count > 0:
            raise serializers.ValidationError("Ya tienes un ticket activo para este servicio")
        
        ticket = Ticket.objects.create(
            user=user,
            service=service,
            priority=priority,
            code=self.generate_code(service)
        )
        return ticket

    def generate_code(self, service):
        import uuid
        return f"{service.name[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
