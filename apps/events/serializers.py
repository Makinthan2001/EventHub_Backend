from rest_framework import serializers
from .models import Category, Event, Ticket, Payment
from apps.accounts.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'image']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'name', 'price', 'total_seats', 'booked_seats', 'is_deleted_field', 'event']
        read_only_fields = ['event']
    
    def validate(self, data):
        total_seats = data.get("total_seats", self.instance.total_seats if self.instance else None)
        booked_seats = data.get("booked_seats", self.instance.booked_seats if self.instance else 0)

        if total_seats is not None and booked_seats > total_seats:
            raise serializers.ValidationError("Booked seats cannot exceed total seats.")
        return data

from django.db import transaction
import json

class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.category_name')
    organizer_name = serializers.ReadOnlyField(source='auth_id.full_name')
    tickets = TicketSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'category_name', 'event_date', 
            'start_time', 'end_time', 'location', 'image', 'is_free', 
            'total_seats', 'booked_seats', 'mobile_number', 'email', 
            'description', 'agenda', 'status', 'auth_id', 
            'organizer_name', 'tickets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'auth_id', 'booked_seats', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # Handle tickets field when it comes as JSON string from FormData
        if isinstance(data.get('tickets'), str):
            try:
                data = data.copy()
                data['tickets'] = json.loads(data['tickets'])
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # Handle agenda field when it comes as JSON string from FormData
        if isinstance(data.get('agenda'), str):
            try:
                data = data.copy()
                data['agenda'] = json.loads(data['agenda'])
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return super().to_internal_value(data)

    def create(self, validated_data):
        tickets_data = validated_data.pop('tickets', [])
        with transaction.atomic():
            event = Event.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(event=event, **ticket_data)
            return event

    def update(self, instance, validated_data):
        tickets_data = validated_data.pop('tickets', None)
        
        with transaction.atomic():
            # Update event fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if tickets_data is not None:
                # Optimized ticket update: Re-create only if needed, 
                # but simple approach for now is atomic delete/create
                instance.tickets.all().delete()
                for ticket_data in tickets_data:
                    Ticket.objects.create(event=instance, **ticket_data)
            
            return instance

    def validate(self, data):
        # Seat capacity validation
        total_seats = data.get("total_seats", self.instance.total_seats if self.instance else 0)
        booked_seats = data.get("booked_seats", self.instance.booked_seats if self.instance else 0)

        if booked_seats > total_seats:
            raise serializers.ValidationError("Booked seats cannot exceed total seats.")

        # Validate tickets based on is_free status
        is_free = data.get('is_free', self.instance.is_free if self.instance else False)
        tickets = data.get('tickets', [])
        
        # If it's a create (no self.instance) or partial update with 'is_free' or 'tickets' provided
        if not is_free and not tickets and not self.instance:
             raise serializers.ValidationError({"tickets": "Paid events must have at least one ticket type."})
        
        start = data.get('start_time')
        end = data.get('end_time')
        if start and end and start >= end:
            raise serializers.ValidationError("Start time must be before end time.")
        return data

class PaymentSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='ticket.event.title')
    event_date = serializers.ReadOnlyField(source='ticket.event.event_date')
    location = serializers.ReadOnlyField(source='ticket.event.location')
    ticket_name = serializers.ReadOnlyField(source='ticket.name')
    
    class Meta:
        model = Payment
        fields = [
            'id', 'full_name', 'mobile_number', 'email', 
            'ticket_count', 'amount', 'ticket', 'transaction_id',
            'created_at', 'event_title', 'event_date', 'location', 'ticket_name'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
