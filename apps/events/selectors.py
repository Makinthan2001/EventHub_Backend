from .models import Event, Payment

def event_list_approved() -> QuerySet:
    return Event.objects.filter(status='approved', is_deleted=False)

def event_list_by_organizer(organizer) -> QuerySet:
    return Event.objects.filter(organizer=organizer, is_deleted=False)

def event_list_pending() -> QuerySet:
    return Event.objects.filter(status='pending', is_deleted=False)

def event_get_stats(event: Event) -> dict:
    payments = Payment.objects.filter(ticket__event=event)
    return {
        'total_registrations': payments.count(),
        'confirmed_registrations': payments.count(), # Assuming all payments are confirmed for now
        'pending_registrations': 0,
        'cancelled_registrations': 0,
        'total_tickets_sold': sum(p.ticket_count for p in payments),
        'total_revenue': sum(p.amount for p in payments),
    }
