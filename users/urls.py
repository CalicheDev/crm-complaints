from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UserListView, UpdateUserRoleView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/update-role/', UpdateUserRoleView.as_view(), name='update-user-role'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
