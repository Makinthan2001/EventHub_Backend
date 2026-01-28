from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    EventViewSet,
    TicketViewSet,
    PaymentViewSet,
)

urlpatterns = [
    # --- CATEGORY ENDPOINTS ---
    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='category-detail'),

    # --- EVENT ENDPOINTS ---
    path('events/', EventViewSet.as_view({'get': 'list', 'post': 'create'}), name='event-list'),
    path('events/my-events/', EventViewSet.as_view({'get': 'my_events'}), name='event-my-events'),
    path('events/<int:pk>/', EventViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='event-detail'),
    path('events/<int:pk>/approve/', EventViewSet.as_view({'post': 'approve'}), name='event-approve'),
    path('events/<int:pk>/reject/', EventViewSet.as_view({'post': 'reject'}), name='event-reject'),

    # --- TICKET ENDPOINTS ---
    path('tickets/', TicketViewSet.as_view({'get': 'list', 'post': 'create'}), name='ticket-list'),
    path('tickets/<int:pk>/', TicketViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='ticket-detail'),

    # --- PAYMENT ENDPOINTS ---
    path('payments/', PaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment-list'),
    path('payments/<int:pk>/', PaymentViewSet.as_view({'get': 'retrieve'}), name='payment-detail'),
]
