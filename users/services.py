import logging
from typing import Dict, List, Optional, Any
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.db import transaction


logger = logging.getLogger(__name__)


class UserService:
    """
    Service class to handle user-related business logic.
    Follows Single Responsibility Principle.
    """
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> tuple[User, str]:
        """
        Create a new user and generate authentication token.
        
        Args:
            user_data: Dictionary containing user registration data
            
        Returns:
            Tuple of (User instance, token string)
        """
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', '')
                )
                
                # Create authentication token
                token, created = Token.objects.get_or_create(user=user)
                
                logger.info(f"New user created: {user.username}")
                return user, token.key
                
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> tuple[Optional[User], Optional[str]]:
        """
        Authenticate user and return user instance with token.
        
        Args:
            username: Username or email
            password: User password
            
        Returns:
            Tuple of (User instance, token string) or (None, None) if failed
        """
        # Try to authenticate with username first
        user = authenticate(username=username, password=password)
        
        # If failed, try with email as username
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            logger.info(f"User authenticated: {user.username}")
            return user, token.key
        
        logger.warning(f"Failed authentication attempt for: {username}")
        return None, None
    
    @staticmethod
    def logout_user(user: User) -> bool:
        """
        Logout user by deleting their token.
        
        Args:
            user: User instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Token.objects.filter(user=user).delete()
            logger.info(f"User logged out: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Error logging out user {user.username}: {str(e)}")
            return False
    
    @staticmethod
    def update_user_profile(user: User, profile_data: Dict[str, Any]) -> User:
        """
        Update user profile information.
        
        Args:
            user: User instance to update
            profile_data: Dictionary containing profile updates
            
        Returns:
            Updated user instance
        """
        try:
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'email']
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            user.save()
            logger.info(f"Profile updated for user: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user.username}: {str(e)}")
            raise
    
    @staticmethod
    def change_password(user: User, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user: User instance
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user.set_password(new_password)
            user.save()
            
            # Invalidate existing tokens to force re-login
            Token.objects.filter(user=user).delete()
            
            logger.info(f"Password changed for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password for user {user.username}: {str(e)}")
            return False


class UserManagementService:
    """
    Service class for admin user management operations.
    """
    
    @staticmethod
    def get_all_users() -> List[User]:
        """
        Get all users with their groups.
        
        Returns:
            List of User instances
        """
        return User.objects.prefetch_related('groups').order_by('-date_joined')
    
    @staticmethod
    def update_user_role(user_id: int, role: str) -> User:
        """
        Update user role by assigning to appropriate group.
        
        Args:
            user_id: ID of the user
            role: Role name ('admin', 'agent', or 'user')
            
        Returns:
            Updated user instance
            
        Raises:
            User.DoesNotExist: If user doesn't exist
            Group.DoesNotExist: If role group doesn't exist
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Clear existing groups
            user.groups.clear()
            
            # Assign new role if not 'user' (regular user has no special groups)
            if role in ['admin', 'agent']:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            
            logger.info(f"Role updated to {role} for user: {user.username}")
            return user
            
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} not found")
            raise
        except Group.DoesNotExist:
            logger.error(f"Group {role} not found")
            raise
        except Exception as e:
            logger.error(f"Error updating role for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    def deactivate_user(user_id: int) -> User:
        """
        Deactivate a user account.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Updated user instance
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            
            # Invalidate user tokens
            Token.objects.filter(user=user).delete()
            
            logger.info(f"User deactivated: {user.username}")
            return user
            
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    def activate_user(user_id: int) -> User:
        """
        Activate a user account.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Updated user instance
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            
            logger.info(f"User activated: {user.username}")
            return user
            
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_user_statistics() -> Dict[str, Any]:
        """
        Get user statistics for admin dashboard.
        
        Returns:
            Dictionary containing user statistics
        """
        try:
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            admin_users = User.objects.filter(groups__name='admin').count()
            agent_users = User.objects.filter(groups__name='agent').count()
            regular_users = total_users - admin_users - agent_users
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'admin_users': admin_users,
                'agent_users': agent_users,
                'regular_users': regular_users,
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            raise