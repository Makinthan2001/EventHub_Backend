"""
SERIALIZERS - Event Management Data validation (Controller layer)
"""
from rest_framework import serializers
from .models import Event, EventAgenda, Ticket, TicketBenefit, EventRegistration
from apps.accounts.serializers import UserSerializer


class EventAgendaSerializer(serializers.ModelSerializer):
    """Serializer for event agenda items"""
    
    class Meta:
        model = EventAgenda
        fields = ['id', 'time', 'title', 'order']


class TicketBenefitSerializer(serializers.ModelSerializer):
    """Serializer for ticket benefits"""
    
    class Meta:
        model = TicketBenefit
        fields = ['id', 'benefit', 'order']


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for ticket types"""
    benefits = TicketBenefitSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'name', 'price', 'available_seats', 'benefits']


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tickets with benefits"""
    benefits = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Ticket
        fields = ['id', 'name', 'price', 'available_seats', 'benefits']
    
    def create(self, validated_data):
        benefits_data = validated_data.pop('benefits', [])
        ticket = Ticket.objects.create(**validated_data)
        
        # Create benefits
        for index, benefit_text in enumerate(benefits_data):
            TicketBenefit.objects.create(
                ticket=ticket,
                benefit=benefit_text,
                order=index
            )
        
        return ticket


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for event list view"""
    organizer_name = serializers.CharField(source='organizer.full_name', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'image', 'event_date', 'event_time',
            'location', 'organizer_name', 'status', 'created_at'
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for event detail view"""
    organizer = UserSerializer(read_only=True)
    agenda_items = EventAgendaSerializer(many=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'image', 'organizer',
            'event_date', 'event_time', 'full_time', 'duration',
            'location', 'full_location',
            'description_intro', 'description_details', 'description_closing', 'description_final_note',
            'audience', 'agenda_items', 'tickets',
            'payment_instructions', 'payment_contact_name', 'payment_contact_email',
            'payment_contact_phone', 'payment_deadline',
            'status', 'created_at', 'updated_at'
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events"""
    agenda = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    tickets = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'image',
            'event_date', 'event_time', 'full_time', 'duration',
            'location', 'full_location',
            'description_intro', 'description_details', 'description_closing', 'description_final_note',
            'audience', 'agenda', 'tickets',
            'payment_instructions', 'payment_contact_name', 'payment_contact_email',
            'payment_contact_phone', 'payment_deadline'
        ]
    
    def create(self, validated_data):
        agenda_data = validated_data.pop('agenda', [])
        tickets_data = validated_data.pop('tickets', [])
        
        # Create event
        event = Event.objects.create(**validated_data)
        
        # Create agenda items
        for index, item in enumerate(agenda_data):
            EventAgenda.objects.create(
                event=event,
                time=item.get('time', ''),
                title=item.get('title', ''),
                order=index
            )
        
        # Create tickets with benefits
        for ticket_data in tickets_data:
            benefits = ticket_data.pop('benefits', [])
            ticket = Ticket.objects.create(event=event, **ticket_data)
            
            for index, benefit in enumerate(benefits):
                TicketBenefit.objects.create(
                    ticket=ticket,
                    benefit=benefit,
                    order=index
                )
        
        return event
    
    def update(self, instance, validated_data):
        agenda_data = validated_data.pop('agenda', None)
        tickets_data = validated_data.pop('tickets', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update agenda if provided
        if agenda_data is not None:
            instance.agenda_items.all().delete()
            for index, item in enumerate(agenda_data):
                EventAgenda.objects.create(
                    event=instance,
                    time=item.get('time', ''),
                    title=item.get('title', ''),
                    order=index
                )
        
        # Update tickets if provided
        if tickets_data is not None:
            instance.tickets.all().delete()
            for ticket_data in tickets_data:
                benefits = ticket_data.pop('benefits', [])
                ticket = Ticket.objects.create(event=instance, **ticket_data)
                
                for index, benefit in enumerate(benefits):
                    TicketBenefit.objects.create(
                        ticket=ticket,
                        benefit=benefit,
                        order=index
                    )
        
        return instance


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for event registrations"""
    event_title = serializers.CharField(source='event.title', read_only=True)
    ticket_name = serializers.CharField(source='ticket.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = EventRegistration
        fields = [
            'id', 'event', 'event_title', 'user', 'user_email', 'ticket', 'ticket_name',
            'full_name', 'email', 'phone', 'number_of_tickets', 'total_amount',
            'special_requests', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Calculate total amount
        ticket = validated_data['ticket']
        number_of_tickets = validated_data['number_of_tickets']
        validated_data['total_amount'] = ticket.price * number_of_tickets
        
        return super().create(validated_data)


class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating event registrations"""
    
    class Meta:
        model = EventRegistration
        fields = [
            'event', 'ticket', 'full_name', 'email', 'phone',
            'number_of_tickets', 'special_requests'
        ]
    
    def validate(self, attrs):
        ticket = attrs['ticket']
        number_of_tickets = attrs['number_of_tickets']
        
        # Check if enough seats available
        booked = ticket.registrations.filter(status='confirmed').aggregate(
            total=models.Sum('number_of_tickets')
        )['total'] or 0
        
        if booked + number_of_tickets > ticket.available_seats:
            raise serializers.ValidationError('Not enough seats available')
        
        return attrs
