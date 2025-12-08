from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime

from .models import Service, Ticket
from .serializers import ServiceSerializer, TicketSerializer, TicketCreateSerializer


class ServiceModelTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name='Atención al Cliente',
            description='Servicio de soporte',
            estimated_duration=15
        )

    def test_service_creation(self):
        self.assertEqual(self.service.name, 'Atención al Cliente')
        self.assertEqual(self.service.estimated_duration, 15)

    def test_service_str(self):
        self.assertEqual(str(self.service), 'Atención al Cliente')


class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123456')
        self.service = Service.objects.create(
            name='Caja',
            estimated_duration=10
        )
        self.ticket = Ticket.objects.create(
            service=self.service,
            user=self.user,
            code='CAJ-ABC123',
            priority='high'
        )

    def test_ticket_creation(self):
        self.assertEqual(self.ticket.code, 'CAJ-ABC123')
        self.assertEqual(self.ticket.status, 'active')
        self.assertEqual(self.ticket.priority, 'high')

    def test_ticket_str(self):
        self.assertEqual(str(self.ticket), 'CAJ-ABC123 - Caja')

    def test_ticket_calculate_estimated_time(self):
        self.ticket.calculate_estimated_time()
        self.assertIsNotNone(self.ticket.estimated_time)


class ServiceSerializerTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name='Test Service',
            estimated_duration=20
        )

    def test_serializer_valid(self):
        data = {
            'name': 'New Service',
            'description': 'Test',
            'estimated_duration': 25
        }
        serializer = ServiceSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class TicketSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123456')
        self.service = Service.objects.create(name='Test', estimated_duration=15)
        self.ticket = Ticket.objects.create(
            service=self.service,
            user=self.user,
            code='TEST-001',
            priority='medium'
        )

    def test_ticket_serializer_valid(self):
        serializer = TicketSerializer(self.ticket)
        self.assertIn('code', serializer.data)
        self.assertIn('status', serializer.data)


class ServiceViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.service = Service.objects.create(
            name='Servicios',
            estimated_duration=10
        )

    def test_get_services(self):
        response = self.client.get('/api/services/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_service(self):
        data = {
            'name': 'New Service',
            'estimated_duration': 15
        }
        response = self.client.post('/api/services/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TicketViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='123456')
        self.service = Service.objects.create(name='Test', estimated_duration=15)
        self.ticket = Ticket.objects.create(
            service=self.service,
            user=self.user,
            code='TEST-001'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_tickets(self):
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_ticket(self):
        response = self.client.post(f'/api/tickets/{self.ticket.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'cancelled')

    def test_mark_called(self):
        response = self.client.post(f'/api/tickets/{self.ticket.id}/mark_called/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'in_service')

    def test_complete_ticket(self):
        self.ticket.status = 'in_service'
        self.ticket.save()
        response = self.client.post(f'/api/tickets/{self.ticket.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'completed')

    def test_user_history(self):
        response = self.client.get('/api/tickets/user_history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ticket_filter_by_status(self):
        response = self.client.get('/api/tickets/?status=active')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ticket_filter_by_priority(self):
        response = self.client.get('/api/tickets/?priority=high')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
