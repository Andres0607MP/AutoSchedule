import django_filters
from .models import Ticket, Service


class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    estimated_duration_gte = django_filters.NumberFilter(
        field_name='estimated_duration',
        lookup_expr='gte'
    )
    estimated_duration_lte = django_filters.NumberFilter(
        field_name='estimated_duration',
        lookup_expr='lte'
    )

    class Meta:
        model = Service
        fields = ['name', 'estimated_duration_gte', 'estimated_duration_lte']


class TicketFilter(django_filters.FilterSet):
    service = django_filters.NumberFilter(field_name='service__id')
    status = django_filters.ChoiceFilter(
        choices=Ticket.STATUS_CHOICES
    )
    priority = django_filters.ChoiceFilter(
        choices=Ticket.PRIORITY_CHOICES
    )
    created_at_gte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_at_lte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    is_called = django_filters.BooleanFilter()
    code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')

    class Meta:
        model = Ticket
        fields = ['service', 'status', 'priority', 'created_at_gte', 'created_at_lte', 'is_called', 'code']
