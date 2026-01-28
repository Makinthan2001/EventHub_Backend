from django.contrib import admin
from .models import Category, Event, Ticket, Payment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name', 'created_at']
    search_fields = ['category_name']


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'auth_id', 'event_date', 'status', 'created_at']
    list_filter = ['category', 'status', 'event_date', 'created_at']
    search_fields = ['title', 'auth_id__email', 'location']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TicketInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'status', 'auth_id', 'is_free')
        }),
        ('Date & Time', {
            'fields': ('event_date', 'start_time', 'end_time')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Contact Info', {
            'fields': ('mobile_number', 'email')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'price', 'total_seats', 'booked_seats', 'created_at']
    list_filter = ['event__category', 'created_at']
    search_fields = ['name', 'event__title']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'full_name', 'ticket', 'amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['transaction_id', 'full_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
