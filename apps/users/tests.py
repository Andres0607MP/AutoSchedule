
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        response = self.client.post('/api/users/register/', {
            'username': 'test',
            'email': 't@test.com',
            'password': '1234'
        }, format='json')
        self.assertEqual(response.status_code, 201)
