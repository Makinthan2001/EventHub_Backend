"""
URL routing for accounts app
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AccountRegistrationView,
    AccountLoginView,
    AccountLogoutView,
    AccountProfileView,
    AccountProfileUpdateView,
    AccountChangePasswordView,
    AdminUserListView,
    AdminUserToggleStatusView,
)

urlpatterns = [
    # Authentication & Session
    path('register/', AccountRegistrationView.as_view(), name='account-register'),
    path('login/', AccountLoginView.as_view(), name='account-login'),
    path('logout/', AccountLogoutView.as_view(), name='account-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Profile Management
    path('profile/', AccountProfileView.as_view(), name='account-profile'),
    path('profile/update/', AccountProfileUpdateView.as_view(), name='account-profile-update'),
    path('change-password/', AccountChangePasswordView.as_view(), name='account-change-password'),
    
    # Admin User Management
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/toggle/', AdminUserToggleStatusView.as_view(), name='admin-user-toggle-status'),
]
