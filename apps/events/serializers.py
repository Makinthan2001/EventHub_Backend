from rest_framework import serializers
from .models import Category, Event, Ticket, Payment
from apps.accounts.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'name', 'price', 'total_seats', 'booked_seats', 'is_deleted_field', 'event']
    
    def validate(self, data):
        if data['booked_seats'] > data['total_seats']:
            raise serializers.ValidationError("Booked seats cannot exceed total seats.")
        return data

class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.category_name')
    organizer_name = serializers.ReadOnlyField(source='auth_id.full_name')
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'category_name', 'event_date', 
            'start_time', 'end_time', 'location', 'is_free', 
            'mobile_number', 'email', 'status', 'auth_id', 'organizer_name',
            'tickets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")
        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'full_name', 'mobile_number', 'email', 
            'ticket_count', 'amount', 'ticket', 'transaction_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
