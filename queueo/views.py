from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction, models
from django.utils import timezone

from .models import Service, Ticket
from .serializers import ServiceSerializer, TicketSerializer, TicketCreateSerializer
from .permissions import IsOwner, IsOwnerOrReadOnly
from .filters import TicketFilter, ServiceFilter
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'estimated_duration', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def agents(self, request, pk=None):
        service = self.get_object()
        active_tickets = service.tickets.filter(status__in=['active', 'in_service']).count()
        return Response({
            'service': service.name,
            'active_tickets': active_tickets,
        })

    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_services = Service.objects.all().annotate(
            ticket_count=models.Count('tickets', filter=models.Q(tickets__status='completed'))
        ).order_by('-ticket_count')[:5]
        
        serializer = self.get_serializer(popular_services, many=True)
        return Response(serializer.data)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['code', 'service__name']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-priority', 'created_at']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_ticket(self, request):
        serializer = TicketCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwner])
    def cancel(self, request, pk=None):
        ticket = self.get_object()
        
        if ticket.status in ['completed', 'cancelled']:
            return Response(
                {'detail': 'No puedes cancelar un ticket completado o ya cancelado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            ticket.status = 'cancelled'
            ticket.save()
        
        return Response({'detail': 'Ticket cancelado exitosamente'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_history(self, request):
        tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
        
        status_param = request.query_params.get('status')
        if status_param:
            tickets = tickets.filter(status=status_param)
        
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_called(self, request, pk=None):
        ticket = self.get_object()
        
        if ticket.status not in ['active', 'in_service']:
            return Response(
                {'detail': 'El ticket no está disponible para ser llamado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            ticket.is_called = True
            ticket.called_at = timezone.now()
            ticket.status = 'in_service'
            ticket.save()
        
        return Response({'detail': 'Ticket marcado como en servicio'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        ticket = self.get_object()
        
        if ticket.status not in ['in_service', 'active']:
            return Response(
                {'detail': 'El ticket no puede ser completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            ticket.status = 'completed'
            ticket.completed_at = timezone.now()
            ticket.save()
        
        return Response({'detail': 'Ticket completado'})


class ServiceListView(ListView):
    model = Service
    template_name = 'queueo/service_list.html'
    context_object_name = 'services'


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'queueo/service_detail.html'
    context_object_name = 'service'


class ServiceCreateView(CreateView):
    model = Service
    fields = ['name', 'description', 'estimated_duration']
    template_name = 'queueo/service_form.html'
    success_url = reverse_lazy('service-list')


class ServiceUpdateView(UpdateView):
    model = Service
    fields = ['name', 'description', 'estimated_duration']
    template_name = 'queueo/service_form.html'
    success_url = reverse_lazy('service-list')


class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'queueo/service_confirm_delete.html'
    success_url = reverse_lazy('service-list')


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'queueo/ticket_list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs.order_by('-created_at')


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'queueo/ticket_detail.html'
    context_object_name = 'ticket'


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = ['service', 'priority']
    template_name = 'queueo/ticket_form.html'
    success_url = reverse_lazy('ticket-list')

    def form_valid(self, form):
        user = self.request.user
        service = form.cleaned_data['service']
        active_count = Ticket.objects.filter(user=user, service=service, status='active').count()
        if active_count > 0:
            form.add_error(None, 'Ya tienes un ticket activo para este servicio')
            return self.form_invalid(form)
        form.instance.user = user
        import uuid
        form.instance.code = f"{service.name[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
        last_position = Ticket.objects.filter(service=service, status='active').count()
        form.instance.position_in_queue = last_position + 1
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    fields = ['status', 'priority']
    template_name = 'queueo/ticket_form.html'
    success_url = reverse_lazy('ticket-list')


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'queueo/ticket_confirm_delete.html'
    success_url = reverse_lazy('ticket-list')
