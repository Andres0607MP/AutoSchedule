import django_filters
from .models import Ticket

class TicketFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Ticket.STATUS_CHOICES)
    service = django_filters.NumberFilter(field_name='service__id')
    class Meta:
        model = Ticket
        fields = ['status','service']
