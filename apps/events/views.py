"""
VIEWS - Event Management API endpoints (Controller layer)
"""
from rest_framework import status, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Event, EventRegistration, Ticket
from .serializers import (
    EventListSerializer,
    EventDetailSerializer,
    EventCreateSerializer,
    EventRegistrationSerializer,
    EventRegistrationCreateSerializer
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission - only owner can edit"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission - only admin can approve/reject"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class EventListCreateView(generics.ListCreateAPIView):
    """
    GET /api/events/ - List all approved events
    POST /api/events/ - Create new event (authenticated users)
    """
    serializer_class = EventListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'category', 'location']
    ordering_fields = ['event_date', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = Event.objects.filter(status='approved')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category and category != 'All Categories':
            queryset = queryset.filter(category=category)
        
        # Filter by date
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(event_date=date)
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location and location != 'All Locations':
            queryset = queryset.filter(Q(location__icontains=location) | Q(full_location__icontains=location))
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user, status='pending')


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/events/<id>/ - Get event details
    PUT/PATCH /api/events/<id>/ - Update event (owner only)
    DELETE /api/events/<id>/ - Delete event (owner only)
    """
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventCreateSerializer
        return EventDetailSerializer
    
    def perform_update(self, serializer):
        # When user edits, set status back to pending
        serializer.save(status='pending')


class MyEventsView(generics.ListAPIView):
    """
    GET /api/events/my-events/ - List events created by current user
    """
    serializer_class = EventListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


class AdminEventApproveView(APIView):
    """
    Endpoint: POST /api/events/<id>/approve/
    Description: Approves a pending event.
    Access: Admin
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.status = 'approved'
        event.save()
        
        return Response({
            'message': 'Event approved successfully',
            'event': EventDetailSerializer(event).data
        }, status=status.HTTP_200_OK)


class AdminEventRejectView(APIView):
    """
    Endpoint: POST /api/events/<id>/reject/
    Description: Rejects a pending event.
    Access: Admin
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.status = 'rejected'
        event.save()
        
        return Response({
            'message': 'Event rejected',
            'event': EventDetailSerializer(event).data
        }, status=status.HTTP_200_OK)


class AdminPendingEventsView(generics.ListAPIView):
    """
    Endpoint: GET /api/events/pending/
    Description: Lists all events awaiting approval.
    Access: Admin
    """
    serializer_class = EventListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Event.objects.filter(status='pending')


class EventRegistrationCreateView(APIView):
    """
    Endpoint: POST /api/events/<event_id>/register/
    Description: Registers the authenticated user for an event.
    Access: Authenticated
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, event_id):
        # We ensure the event_id in URL matches the one in data if provided
        # but the serializer handles the core logic.
        serializer = EventRegistrationCreateSerializer(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            registration = serializer.save()
            return Response({
                'message': 'Registration successful',
                'registration': EventRegistrationSerializer(registration).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyRegistrationsView(generics.ListAPIView):
    """
    GET /api/events/my-registrations/ - List user's event registrations
    """
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user)


class EventRegistrationsView(generics.ListAPIView):
    """
    GET /api/events/<event_id>/registrations/ - List registrations for an event (owner/admin only)
    """
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, pk=event_id)
        
        # Only event owner or admin can view registrations
        if event.organizer != self.request.user and not self.request.user.is_staff:
            return EventRegistration.objects.none()
        
        return EventRegistration.objects.filter(event=event)


class EventStatsView(APIView):
    """
    GET /api/events/<event_id>/stats/ - Get event statistics (owner/admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        
        # Only event owner or admin can view stats
        if event.organizer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        registrations = EventRegistration.objects.filter(event=event)
        
        stats = {
            'total_registrations': registrations.count(),
            'confirmed_registrations': registrations.filter(status='confirmed').count(),
            'pending_registrations': registrations.filter(status='pending').count(),
            'cancelled_registrations': registrations.filter(status='cancelled').count(),
            'total_tickets_sold': sum(r.number_of_tickets for r in registrations.filter(status='confirmed')),
            'total_revenue': sum(r.total_amount for r in registrations.filter(status='confirmed')),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
