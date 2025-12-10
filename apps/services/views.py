from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from .models import Service
from .serializers import (
    AssignAgentsSerializer,
    AgentSerializer,
)

class AssignAgentsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        service = generics.get_object_or_404(Service, pk=pk)
        serializer = AssignAgentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent_ids = serializer.validated_data["agents"]
        service.agents.set(agent_ids)
        service.save()

        return Response({
            "service_id": service.id,
            "assigned_agents": agent_ids
        })
