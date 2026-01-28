from django.contrib import admin
from .models import Event, EventAgenda, Ticket, TicketBenefit, EventRegistration


class EventAgendaInline(admin.TabularInline):
    model = EventAgenda
    extra = 1


class TicketInline(admin.StackedInline):
    model = Ticket
    extra = 1


class TicketBenefitInline(admin.TabularInline):
    model = TicketBenefit
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'organizer', 'event_date', 'status', 'created_at']
    list_filter = ['category', 'status', 'event_date', 'created_at']
    search_fields = ['title', 'organizer__email', 'location']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EventAgendaInline, TicketInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'image', 'organizer', 'status')
        }),
        ('Date & Time', {
            'fields': ('event_date', 'event_time', 'full_time', 'duration')
        }),
        ('Location', {
            'fields': ('location', 'full_location')
        }),
        ('Description', {
            'fields': ('description_intro', 'description_details', 'description_closing', 'description_final_note')
        }),
        ('Additional Information', {
            'fields': ('audience', 'payment_instructions', 'payment_contact_name', 'payment_contact_email', 'payment_contact_phone', 'payment_deadline')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'price', 'available_seats', 'created_at']
    list_filter = ['event__category', 'created_at']
    search_fields = ['name', 'event__title']
    inlines = [TicketBenefitInline]


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'ticket', 'number_of_tickets', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'event__category']
    search_fields = ['user__email', 'event__title', 'full_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Registration Info', {
            'fields': ('event', 'user', 'ticket', 'status')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Ticket Information', {
            'fields': ('number_of_tickets', 'total_amount')
        }),
        ('Additional', {
            'fields': ('special_requests',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
