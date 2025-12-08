from django.contrib import admin
from .models import Service, Ticket


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'estimated_duration', 'created_at')
	search_fields = ('name', 'description')
	list_filter = ('estimated_duration',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
	list_display = ('id', 'code', 'service', 'user', 'status', 'priority', 'created_at')
	search_fields = ('code', 'service__name', 'user__username', 'user__email')
	list_filter = ('status', 'priority', 'service')
	readonly_fields = ('created_at', 'called_at', 'completed_at')
