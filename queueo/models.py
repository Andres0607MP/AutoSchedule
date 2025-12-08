from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    estimated_duration = models.IntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('cancelled', 'Cancelado'),
        ('completed', 'Completado'),
        ('in_service', 'En Atención'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    estimated_time = models.DateTimeField(null=True, blank=True)
    is_called = models.BooleanField(default=False)
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='medium')
    position_in_queue = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['service', 'status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.service.name}"
    
    def calculate_estimated_time(self):
        if not self.estimated_time:
            position = self.position_in_queue
            duration_minutes = self.service.estimated_duration
            self.estimated_time = timezone.now() + timedelta(minutes=position * duration_minutes)
            self.save(update_fields=['estimated_time'])
        return self.estimated_time
