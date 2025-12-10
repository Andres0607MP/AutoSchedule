from rest_framework import serializers
from users.models import Profile
from .models import Service

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "user", "role"]

class AssignAgentsSerializer(serializers.Serializer):
    agents = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_agents(self, value):
        from users.models import Profile

        agents = Profile.objects.filter(id__in=value, role="agent")
        if agents.count() != len(value):
            raise serializers.ValidationError(
                "Uno o más IDs no corresponden a perfiles con rol 'agent'."
            )
        return value
