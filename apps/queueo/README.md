queueo app (Option A) - basic phase 2
-----------------------------------
Files:
- models.py (Service, Ticket)
- serializers.py (ServiceSerializer, TicketSerializer, TicketCreateSerializer)
- views.py (ViewSets + create_ticket, cancel, user_history)
- filters.py (TicketFilter)
- permissions.py (IsOwnerOrReadOnly)
- urls.py (router for services and tickets)
- admin.py (register models)
- tests.py (basic tests)

Installation:
1. Copy `queueo` folder into your project root.
2. Add 'queueo' to INSTALLED_APPS in settings.py
3. Install dependencies: django, djangorestframework, django-filter
4. Run: python manage.py makemigrations queueo
5. Run: python manage.py migrate
6. Start server and test endpoints.
