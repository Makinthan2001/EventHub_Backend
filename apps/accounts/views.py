"""
VIEWS - API endpoints (Controller layer)
"""
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class AccountRegistrationView(APIView):
    """
    Endpoint: POST /api/auth/register/
    Description: Registers a new user and returns JWT tokens.
    Access: Public
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountLoginView(APIView):
    """
    Endpoint: POST /api/auth/login/
    Description: Authenticates user and returns JWT tokens.
    Access: Public
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountLogoutView(APIView):
    """
    Endpoint: POST /api/auth/logout/
    Description: Blacklists the provided refresh token.
    Access: Authenticated
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AccountProfileView(APIView):
    """
    Endpoint: GET /api/auth/profile/
    Description: Retrieves the current user's profile details.
    Access: Authenticated
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountProfileUpdateView(APIView):
    """
    Endpoint: PUT/PATCH /api/auth/profile/update/
    Description: Updates the current user's profile information.
    Access: Authenticated
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': UserSerializer(request.user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        return self.put(request)


class AccountChangePasswordView(APIView):
    """
    Endpoint: POST /api/auth/change-password/
    Description: Changes the password for the current user.
    Access: Authenticated
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Wrong password']}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserListView(generics.ListAPIView):
    """
    Endpoint: GET /api/auth/users/
    Description: Lists all users in the system.
    Access: Admin
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminUserToggleStatusView(APIView):
    """
    Endpoint: PATCH /api/auth/users/<id>/toggle/
    Description: Toggles the is_active status of a user.
    Access: Admin
    """
    permission_classes = [permissions.IsAdminUser]
    
    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_active = not user.is_active
            user.save()
            return Response({
                'message': f'User {"enabled" if user.is_active else "disabled"} successfully',
                'is_active': user.is_active
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class AdminUserChangeRoleView(APIView):
    """
    Endpoint: PATCH /api/auth/users/<id>/role/
    Description: Changes the role of a user.
    Access: Admin
    """
    permission_classes = [permissions.IsAdminUser]
    
    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            role = request.data.get('role')
            if role not in dict(User.ROLE_CHOICES):
                return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.role = role
            # Sync is_staff with admin role
            user.is_staff = (role == 'admin')
            user.save()
            return Response({
                'message': f'User role updated to {role} successfully',
                'role': user.role,
                'is_staff': user.is_staff
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
