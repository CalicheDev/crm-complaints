import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth.models import User

from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    PasswordChangeSerializer, UserListSerializer, UserRoleUpdateSerializer, TokenSerializer
)
from .services import UserService, UserManagementService
from complaints.permissions import IsAdminUser


logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    """
    Register a new user.
    Public endpoint with throttling to prevent abuse.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        """Register a new user."""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user, token = UserService.create_user(serializer.validated_data)
            
            response_serializer = TokenSerializer({
                'token': token,
                'user': user
            })
            
            return Response({
                'message': 'User registered successfully.',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'error': 'Registration failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    """
    User login endpoint.
    Returns authentication token on successful login.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        """Authenticate user and return token."""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user, token = UserService.authenticate_user(username, password)
            
            if user and token:
                response_serializer = TokenSerializer({
                    'token': token,
                    'user': user
                })
                
                return Response({
                    'message': 'Login successful.',
                    'data': response_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials or account inactive.'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'error': 'Login failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    """
    User logout endpoint.
    Invalidates the user's authentication token.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Logout user by invalidating token."""
        try:
            success = UserService.logout_user(request.user)
            
            if success:
                return Response({
                    'message': 'Logout successful.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Logout failed.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Logout failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile.
    Users can only access their own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current user."""
        return self.request.user
    
    def perform_update(self, serializer):
        """Update user profile using service layer."""
        try:
            user = UserService.update_user_profile(
                self.request.user,
                serializer.validated_data
            )
            serializer.instance = user
            
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            raise


class PasswordChangeView(APIView):
    """
    Change user password.
    Requires current password for security.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    
    def post(self, request):
        """Change user password."""
        try:
            serializer = self.serializer_class(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            
            success = UserService.change_password(
                request.user,
                serializer.validated_data['new_password']
            )
            
            if success:
                return Response({
                    'message': 'Password changed successfully. Please login again.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Password change failed.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return Response({
                'error': 'Password change failed. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(generics.ListAPIView):
    """
    List all users (admin only).
    Provides comprehensive user information for management.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Get all users with related data."""
        return UserManagementService.get_all_users()


class UserRoleUpdateView(APIView):
    """
    Update user role (admin only).
    Allows admins to assign roles to users.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserRoleUpdateSerializer
    
    def post(self, request, user_id):
        """Update user role."""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = UserManagementService.update_user_role(
                user_id,
                serializer.validated_data['role']
            )
            
            response_serializer = UserListSerializer(user)
            return Response({
                'message': f'Role updated successfully.',
                'user': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Role update error: {str(e)}")
            return Response({
                'error': 'Role update failed.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserActivationView(APIView):
    """
    Activate/deactivate user account (admin only).
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, user_id):
        """Activate user account."""
        try:
            user = UserManagementService.activate_user(user_id)
            response_serializer = UserListSerializer(user)
            
            return Response({
                'message': 'User activated successfully.',
                'user': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"User activation error: {str(e)}")
            return Response({
                'error': 'User activation failed.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, user_id):
        """Deactivate user account."""
        try:
            user = UserManagementService.deactivate_user(user_id)
            response_serializer = UserListSerializer(user)
            
            return Response({
                'message': 'User deactivated successfully.',
                'user': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"User deactivation error: {str(e)}")
            return Response({
                'error': 'User deactivation failed.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStatisticsView(APIView):
    """
    Get user statistics for admin dashboard.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get user statistics."""
        try:
            statistics = UserManagementService.get_user_statistics()
            
            return Response({
                'statistics': statistics
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"User statistics error: {str(e)}")
            return Response({
                'error': 'Failed to retrieve user statistics.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)