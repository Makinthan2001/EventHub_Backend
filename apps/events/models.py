"""
MODELS - Event Management Database Schema using Django ORM
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Event(models.Model):
    """Event model - Main event information"""
    
    CATEGORY_CHOICES = [
        ('Music', 'Music'),
        ('Tech', 'Tech'),
        ('Education', 'Education'),
        ('Sports', 'Sports'),
        ('Business', 'Business'),
        ('Art', 'Art'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.URLField(max_length=500, blank=True, null=True)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    
    # Date and Time
    event_date = models.DateField()
    event_time = models.TimeField()
    full_time = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    
    # Location
    location = models.CharField(max_length=255)
    full_location = models.TextField(blank=True, null=True)
    
    # Description
    description_intro = models.TextField(blank=True, null=True)
    description_details = models.TextField(blank=True, null=True)
    description_closing = models.TextField(blank=True, null=True)
    description_final_note = models.TextField(blank=True, null=True)
    
    # Target Audience
    audience = models.TextField(blank=True, null=True)
    
    # Payment Information
    payment_instructions = models.TextField(blank=True, null=True)
    payment_contact_name = models.CharField(max_length=255, blank=True, null=True)
    payment_contact_email = models.EmailField(blank=True, null=True)
    payment_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    payment_deadline = models.CharField(max_length=255, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['event_date']),
            models.Index(fields=['organizer']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_upcoming(self):
        return self.event_date >= timezone.now().date()


class EventAgenda(models.Model):
    """Event agenda/schedule items"""
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='agenda_items')
    time = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'event_agenda'
        verbose_name = 'Event Agenda Item'
        verbose_name_plural = 'Event Agenda Items'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.event.title} - {self.time}: {self.title}"


class Ticket(models.Model):
    """Ticket types for events"""
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_seats = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.event.title} - {self.name}"
    
    @property
    def is_available(self):
        booked = self.registrations.filter(status='confirmed').count()
        return booked < self.available_seats


class TicketBenefit(models.Model):
    """Benefits for each ticket type"""
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='benefits')
    benefit = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'ticket_benefits'
        verbose_name = 'Ticket Benefit'
        verbose_name_plural = 'Ticket Benefits'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.ticket.name} - {self.benefit}"


class EventRegistration(models.Model):
    """User registration for events"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='registrations')
    
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Ticket Information
    number_of_tickets = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional Information
    special_requests = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_registrations'
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'
        ordering = ['-created_at']
        unique_together = ['event', 'user', 'ticket']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['event', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.event.title}"
