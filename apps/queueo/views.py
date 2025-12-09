from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from .models import Service, Ticket
from .serializers import ServiceSerializer, TicketSerializer, TicketCreateSerializer
from .permissions import IsOwnerOrReadOnly
from .filters import TicketFilter

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = []  # open read/write; change if needed
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name','description']

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['code','service__name']
    ordering_fields = ['created_at','status']

    def get_serializer_class(self):
        if self.action in ('create','create_ticket'):
            return TicketCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_ticket(self, request):
        serializer = TicketCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            ticket = serializer.save()
            return Response(TicketSerializer(ticket, context={'request':request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly])
    def cancel(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status in ['cancelled','completed']:
            return Response({'detail':'Ticket no puede ser cancelado'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            ticket.status = 'cancelled'
            ticket.save()
        return Response({'detail':'Ticket cancelado'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_history(self, request):
        qs = Ticket.objects.filter(user=request.user).order_by('-created_at')
        status_q = request.query_params.get('status')
        if status_q:
            qs = qs.filter(status=status_q)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = TicketSerializer(page, many=True, context={'request':request})
            return self.get_paginated_response(serializer.data)
        serializer = TicketSerializer(qs, many=True, context={'request':request})
        return Response(serializer.data)
