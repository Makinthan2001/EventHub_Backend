from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Event, EventAgenda, Ticket, TicketBenefit, EventRegistration

@transaction.atomic
def event_create(*, organizer, **data) -> Event:
    agenda_data = data.pop('agenda_items', [])
    tickets_data = data.pop('tickets', [])
    
    event = Event.objects.create(organizer=organizer, status='pending', **data)
    
    for item in agenda_data:
        EventAgenda.objects.create(event=event, **item)
        
    for ticket_data in tickets_data:
        benefits_data = ticket_data.pop('benefits', [])
        ticket = Ticket.objects.create(event=event, **ticket_data)
        for benefit in benefits_data:
            TicketBenefit.objects.create(ticket=ticket, **benefit)
            
    return event

@transaction.atomic
def event_update(*, event: Event, data) -> Event:
    # Basic logic for now, can be expanded to handle agenda/tickets updates
    for field, value in data.items():
        setattr(event, field, value)
    
    event.status = 'pending'  # Re-verify on edit
    event.save()
    return event

def event_approve(*, event: Event) -> Event:
    event.status = 'approved'
    event.save(update_fields=['status'])
    return event

def event_reject(*, event: Event) -> Event:
    event.status = 'rejected'
    event.save(update_fields=['status'])
    return event

@transaction.atomic
def event_registration_create(*, user, event, ticket, **data) -> EventRegistration:
    if not ticket.is_available:
        raise ValidationError("Selected ticket is sold out.")
        
    registration = EventRegistration.objects.create(
        user=user,
        event=event,
        ticket=ticket,
        **data
    )
    return registration
