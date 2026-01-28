from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AccountRegistrationView,
    AccountLoginView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Authentication
    path('register/', AccountRegistrationView.as_view(), name='account-register'),
    path('login/', AccountLoginView.as_view(), name='account-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Management API
    path('', include(router.urls)),
]
