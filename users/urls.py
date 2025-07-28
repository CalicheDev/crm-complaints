from django.urls import path
from .views import (
    UserRegistrationView, LoginView, LogoutView, UserProfileView,
    PasswordChangeView, UserListView, UserRoleUpdateView,
    UserActivationView, UserStatisticsView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', PasswordChangeView.as_view(), name='user-change-password'),
    
    # Admin user management endpoints
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/role/', UserRoleUpdateView.as_view(), name='user-role-update'),
    path('users/<int:user_id>/activation/', UserActivationView.as_view(), name='user-activation'),
    path('users/statistics/', UserStatisticsView.as_view(), name='user-statistics'),
]
