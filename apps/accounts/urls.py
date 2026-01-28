from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AccountRegistrationView,
    AccountLoginView,
    UserViewSet,
)

urlpatterns = [
    # Authentication
    path('register/', AccountRegistrationView.as_view(), name='account-register'),
    path('login/', AccountLoginView.as_view(), name='account-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Management API
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='user-detail'),
]
