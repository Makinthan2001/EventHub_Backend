from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import json

from .models import Category, Event, Ticket, Payment
from .serializers import CategorySerializer, EventSerializer, TicketSerializer, PaymentSerializer
from apps.accounts.permissions import IsAdminRole

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category_name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_free', 'auth_id']
    search_fields = ['title', 'location', 'email']
    ordering_fields = ['event_date', 'created_at']

    @action(detail=False, methods=['get'], url_path='my-events')
    def my_events(self, request):
        """Get events created by the current user"""
        events = self.queryset.filter(auth_id=request.user)
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action in ['approve', 'reject']:
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # Handle JSON fields from FormData
        data = {}
        for key, value in request.data.items():
            data[key] = value
        
        # Parse JSON strings for agenda and tickets
        if 'agenda' in data and isinstance(data['agenda'], str):
            try:
                data['agenda'] = json.loads(data['agenda']) if data['agenda'] else []
            except (json.JSONDecodeError, ValueError):
                data['agenda'] = []
        elif 'agenda' not in data:
            data['agenda'] = []
        
        if 'tickets' in data and isinstance(data['tickets'], str):
            try:
                data['tickets'] = json.loads(data['tickets']) if data['tickets'] else []
            except (json.JSONDecodeError, ValueError):
                data['tickets'] = []
        elif 'tickets' not in data:
            data['tickets'] = []
        
        # Handle image file separately
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # Handle JSON fields from FormData
        data = {}
        for key, value in request.data.items():
            data[key] = value
        
        # Parse JSON strings for agenda and tickets
        if 'agenda' in data and isinstance(data['agenda'], str):
            try:
                data['agenda'] = json.loads(data['agenda']) if data['agenda'] else []
            except (json.JSONDecodeError, ValueError):
                data['agenda'] = []
        
        if 'tickets' in data and isinstance(data['tickets'], str):
            try:
                data['tickets'] = json.loads(data['tickets']) if data['tickets'] else []
            except (json.JSONDecodeError, ValueError):
                data['tickets'] = []
        
        # Handle image file separately
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(auth_id=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def approve(self, request, pk=None):
        event = self.get_object()
        event.status = 'accepted'
        event.save()
        return Response({'status': 'event accepted'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def reject(self, request, pk=None):
        event = self.get_object()
        event.status = 'rejected'
        event.save()
        return Response({'status': 'event rejected'})

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'is_deleted_field']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ticket', 'email', 'ticket__event']
    search_fields = ['transaction_id', 'full_name', 'email']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        return self.queryset.filter(ticket__event__auth_id=user)

    def perform_create(self, serializer):
        from django.db import transaction
        from django.shortcuts import get_object_or_404
        
        with transaction.atomic():
            ticket_id = self.request.data.get('ticket')
            ticket_count = int(self.request.data.get('ticket_count', 1))
            ticket = get_object_or_404(Ticket, id=ticket_id)
            event = ticket.event

            # Check for generic event seat availability if applicable
            if event.total_seats > 0 and (event.booked_seats + ticket_count) > event.total_seats:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Not enough seats available for this event.")

            # Check for specific ticket seat availability
            if (ticket.booked_seats + ticket_count) > ticket.total_seats:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Not enough slots available for this ticket type.")

            # Increment booked seats
            ticket.booked_seats += ticket_count
            ticket.save()
            
            event.booked_seats += ticket_count
            event.save()

            serializer.save()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get total revenue and transaction count"""
        queryset = self.filter_queryset(self.get_queryset())
        from django.db.models import Sum, Count
        summary_data = queryset.aggregate(
            total_revenue=Sum('amount'),
            total_transactions=Count('id')
        )
        return Response({
            'total_revenue': summary_data['total_revenue'] or 0,
            'total_transactions': summary_data['total_transactions'] or 0
        })
