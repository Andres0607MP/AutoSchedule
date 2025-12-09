
from django.urls import path
from .views import RegisterView, ProfileMeView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('me/', ProfileMeView.as_view()),
]
