from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
	ServiceViewSet,
	TicketViewSet,
	ServiceListView,
	ServiceCreateView,
	ServiceUpdateView,
	ServiceDeleteView,
	ServiceDetailView,
	TicketListView,
	TicketCreateView,
	TicketUpdateView,
	TicketDeleteView,
	TicketDetailView,
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'tickets', TicketViewSet)

urlpatterns = router.urls + [
	path('web/services/', ServiceListView.as_view(), name='service-list'),
	path('web/services/create/', ServiceCreateView.as_view(), name='service-create'),
	path('web/services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
	path('web/services/<int:pk>/edit/', ServiceUpdateView.as_view(), name='service-update'),
	path('web/services/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service-delete'),

	path('web/tickets/', TicketListView.as_view(), name='ticket-list'),
	path('web/tickets/create/', TicketCreateView.as_view(), name='ticket-create'),
	path('web/tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
	path('web/tickets/<int:pk>/edit/', TicketUpdateView.as_view(), name='ticket-update'),
	path('web/tickets/<int:pk>/delete/', TicketDeleteView.as_view(), name='ticket-delete'),
]
