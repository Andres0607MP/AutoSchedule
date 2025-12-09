from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ServiceViewSet, TicketViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'tickets', TicketViewSet)

urlpatterns = router.urls + [
    path('', lambda request: None),  # placeholder if needed
]
