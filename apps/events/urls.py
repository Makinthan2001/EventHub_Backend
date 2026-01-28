"""
URL routing for events app
"""
from django.urls import path
from .views import (
    EventListCreateView,
    EventDetailView,
    MyEventsView,
    AdminEventApproveView,
    AdminEventRejectView,
    AdminPendingEventsView,
    EventRegistrationCreateView,
    MyRegistrationsView,
    EventRegistrationsView,
    EventStatsView,
)

urlpatterns = [
    # Core Event API
    path('', EventListCreateView.as_view(), name='event-list-create'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('my-events/', MyEventsView.as_view(), name='event-my-list'),
    
    # Registration & Attendance
    path('<int:event_id>/register/', EventRegistrationCreateView.as_view(), name='event-registration-create'),
    path('my-registrations/', MyRegistrationsView.as_view(), name='event-my-registrations'),
    path('<int:event_id>/registrations/', EventRegistrationsView.as_view(), name='event-registration-list'),
    path('<int:event_id>/stats/', EventStatsView.as_view(), name='event-stats'),
    
    # Administrative Actions
    path('pending/', AdminPendingEventsView.as_view(), name='admin-event-pending-list'),
    path('<int:pk>/approve/', AdminEventApproveView.as_view(), name='admin-event-approve'),
    path('<int:pk>/reject/', AdminEventRejectView.as_view(), name='admin-event-reject'),
]
