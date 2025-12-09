from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Service, Ticket

class QueueoBasicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='tester', password='1234')
        self.service = Service.objects.create(name='Soporte')

    def test_create_ticket_endpoint_requires_auth(self):
        resp = self.client.post('/api/tickets/create_ticket/', {'service': self.service.id}, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_create_ticket(self):
        self.client.login(username='tester', password='1234')
        resp = self.client.post('/api/tickets/create_ticket/', {'service': self.service.id}, format='json')
        self.assertIn(resp.status_code, (200,201))
