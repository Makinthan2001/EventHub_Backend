"""
URL routing for events app
"""
from django.urls import path
from .views import (
    EventListCreateView,
    EventDetailView,
    MyEventsView,
    EventApproveView,
    EventRejectView,
    PendingEventsView,
    EventRegistrationCreateView,
    MyRegistrationsView,
    EventRegistrationsView,
    EventStatsView,
)

urlpatterns = [
    # Event CRUD
    path('', EventListCreateView.as_view(), name='event-list-create'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('my-events/', MyEventsView.as_view(), name='my-events'),
    
    # Admin - Event Approval
    path('pending/', PendingEventsView.as_view(), name='pending-events'),
    path('<int:pk>/approve/', EventApproveView.as_view(), name='event-approve'),
    path('<int:pk>/reject/', EventRejectView.as_view(), name='event-reject'),
    
    # Event Registration
    path('<int:event_id>/register/', EventRegistrationCreateView.as_view(), name='event-register'),
    path('my-registrations/', MyRegistrationsView.as_view(), name='my-registrations'),
    path('<int:event_id>/registrations/', EventRegistrationsView.as_view(), name='event-registrations'),
    path('<int:event_id>/stats/', EventStatsView.as_view(), name='event-stats'),
]
