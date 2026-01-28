from django.db.models import QuerySet, Q
from .models import Event, EventRegistration

def event_list_approved() -> QuerySet:
    return Event.objects.filter(status='approved', is_deleted=False)

def event_list_by_organizer(organizer) -> QuerySet:
    return Event.objects.filter(organizer=organizer, is_deleted=False)

def event_list_pending() -> QuerySet:
    return Event.objects.filter(status='pending', is_deleted=False)

def event_get_stats(event: Event) -> dict:
    registrations = EventRegistration.objects.filter(event=event)
    return {
        'total_registrations': registrations.count(),
        'confirmed_registrations': registrations.filter(status='confirmed').count(),
        'pending_registrations': registrations.filter(status='pending').count(),
        'cancelled_registrations': registrations.filter(status='cancelled').count(),
        'total_tickets_sold': sum(r.number_of_tickets for r in registrations.filter(status='confirmed')),
        'total_revenue': sum(r.total_amount for r in registrations.filter(status='confirmed')),
    }
