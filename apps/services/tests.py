import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from services.models import Service

@pytest.mark.django_db
def test_filter_by_name():
    Service.objects.create(name="Asesoría", category="general", estimated_duration=10)
    Service.objects.create(name="Caja rápida", category="banco", estimated_duration=5)

    client = APIClient()
    user = User.objects.create_user("demo", "demo@test.com", "123456")
    client.force_authenticate(user)

    response = client.get("/api/services/?name=caja")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Caja rápida"
