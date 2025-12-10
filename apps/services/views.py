from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from users.models import Profile
from .filters import ServiceFilter
from .models import Service
from .serializers import (
    AgentSerializer,
    AssignAgentsSerializer,
    ServiceSerializer,
)
from .swagger import service_list_docs


# =========================================================
# PERMISOS PARA CRUD DE SERVICIOS (S3)
# =========================================================
class IsAdminOrReadOnly(permissions.BasePermission):
    """Admins pueden crear/editar/borrar. Usuarios autenticados solo leer."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


# =========================================================
# LISTAR AGENTES DE UN SERVICIO (GET /services/<id>/agents/)
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def service_agents(request, pk):
    """Lista los agentes asignados a un servicio."""
    service = get_object_or_404(Service, pk=pk)
    users_qs = service.agents.all()
    profiles_qs = Profile.objects.filter(user__in=users_qs, role="agent")

    data = {
        "service": service.name,
        "agents": AgentSerializer(profiles_qs, many=True).data,
    }
    return Response(data, status=status.HTTP_200_OK)


# =========================================================
# ASIGNAR AGENTES A UN SERVICIO (POST /services/<id>/assign-agents/)
# =========================================================
@api_view(["POST"])
@permission_classes([IsAdminUser])
def assign_agents(request, pk):
    """Asigna agentes (perfiles con rol 'agent') a un servicio."""
    service = get_object_or_404(Service, pk=pk)
    serializer = AssignAgentsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    profile_ids = serializer.validated_data["agents"]
    profiles_qs = Profile.objects.filter(id__in=profile_ids, role="agent")

    user_ids = profiles_qs.values_list("user_id", flat=True)
    service.agents.set(user_ids)

    data = {
        "message": "Agentes asignados correctamente",
        "service": service.name,
        "agents": AgentSerializer(profiles_qs, many=True).data,
    }
    return Response(data, status=status.HTTP_200_OK)


# =========================================================
# LISTAR Y CREAR SERVICIOS (GET/POST /services/)
# =========================================================
class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServiceFilter

    @service_list_docs
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# =========================================================
# DETALLE, EDITAR Y BORRAR SERVICIO (GET/PUT/DELETE)
# =========================================================
class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
