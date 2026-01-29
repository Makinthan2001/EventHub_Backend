from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Event, Ticket, Payment, EventAgenda, TicketBenefit

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
    event.status = 'accepted'
    event.save(update_fields=['status'])
    return event

def event_reject(*, event: Event) -> Event:
    event.status = 'rejected'
    event.save(update_fields=['status'])
    return event

@transaction.atomic
def event_registration_create(*, ticket_id, ticket_count=1, **data) -> Payment:
    ticket = get_object_or_404(Ticket, id=ticket_id)
    event = ticket.event

    # Check for generic event seat availability if applicable
    if event.total_seats > 0 and (event.booked_seats + ticket_count) > event.total_seats:
        raise ValidationError("Not enough seats available for this event.")

    # Check for specific ticket seat availability
    if (ticket.booked_seats + ticket_count) > ticket.total_seats:
        raise ValidationError("Not enough slots available for this ticket type.")

    # Increment booked seats
    ticket.booked_seats += ticket_count
    ticket.save()
    
    event.booked_seats += ticket_count
    event.save()

    registration = Payment.objects.create(
        ticket=ticket,
        ticket_count=ticket_count,
        **data
    )
    return registration
