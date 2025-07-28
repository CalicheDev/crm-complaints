from rest_framework import permissions
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group


class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='admin').exists()
        )


class IsAgentUser(BasePermission):
    """
    Custom permission to only allow agent users to access certain views.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='agent').exists()
        )


class IsAdminOrAgent(BasePermission):
    """
    Custom permission to allow admin or agent users to access certain views.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.groups.filter(name__in=['admin', 'agent']).exists() or 
             request.user.is_superuser)
        )


class IsOwnerOrAdminOrAgent(BasePermission):
    """
    Custom permission to only allow owners of an object, admins, or agents to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only to the owner, admin, or agent
        return (
            obj.created_by == request.user or
            request.user.groups.filter(name__in=['admin', 'agent']).exists() or
            request.user.is_superuser
        )


class CanAssignComplaint(BasePermission):
    """
    Permission to assign complaints to agents. Only admins can do this.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.groups.filter(name='admin').exists() or 
             request.user.is_superuser)
        )


class CanViewDashboard(BasePermission):
    """
    Permission to view dashboard analytics. Only admins can do this.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.groups.filter(name='admin').exists() or 
             request.user.is_superuser)
        )