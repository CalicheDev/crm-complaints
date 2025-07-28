import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Complaint
from .serializers import (
    ComplaintListSerializer, ComplaintDetailSerializer, ComplaintCreateSerializer,
    ComplaintAssignSerializer, ComplaintStatusUpdateSerializer, DashboardAnalyticsSerializer
)
from .permissions import (
    IsAdminUser, IsAgentUser, IsAdminOrAgent, IsOwnerOrAdminOrAgent,
    CanAssignComplaint, CanViewDashboard
)
from .services import ComplaintService, DashboardService
from .exceptions import (
    ComplaintServiceError, ComplaintNotFoundError, AgentNotFoundError
)


logger = logging.getLogger(__name__)


class ComplaintListCreateView(generics.ListCreateAPIView):
    """
    List complaints or create a new complaint.
    - GET: List all complaints (authenticated users see all, anonymous see only public)
    - POST: Create a new complaint (anonymous allowed)
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ComplaintCreateSerializer
        return ComplaintListSerializer
    
    def get_queryset(self):
        """Filter complaints based on user permissions."""
        queryset = Complaint.objects.select_related('created_by', 'assigned_to')
        
        if not self.request.user.is_authenticated:
            # Anonymous users can only see their own anonymous complaints
            # For now, show all pending complaints for public visibility
            return queryset.filter(status='pending').order_by('-created_at')
        
        # Authenticated users
        user = self.request.user
        
        # Admins can see all complaints
        if user.groups.filter(name='admin').exists() or user.is_superuser:
            return queryset.order_by('-created_at')
        
        # Agents can see assigned complaints and unassigned ones
        if user.groups.filter(name='agent').exists():
            return queryset.filter(
                Q(assigned_to=user) | Q(assigned_to__isnull=True)
            ).order_by('-created_at')
        
        # Regular users can see their own complaints
        return queryset.filter(created_by=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a new complaint using the service layer."""
        try:
            user = self.request.user if self.request.user.is_authenticated else None
            complaint = ComplaintService.create_complaint(
                serializer.validated_data, 
                user
            )
            # Return the created complaint data
            serializer.instance = complaint
            
        except ComplaintServiceError as e:
            logger.error(f"Error creating complaint: {str(e)}")
            raise


class ComplaintDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a complaint.
    - GET: Anyone authenticated can view
    - PUT/PATCH: Only owner, admin, or assigned agent can update
    - DELETE: Only admin can delete
    """
    serializer_class = ComplaintDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrAgent]
    
    def get_queryset(self):
        return Complaint.objects.select_related('created_by', 'assigned_to')
    
    def perform_update(self, serializer):
        """Handle complaint updates with proper logging."""
        complaint = serializer.save()
        logger.info(
            f"Complaint {complaint.id} updated by user {self.request.user.username}"
        )
    
    def perform_destroy(self, instance):
        """Only admins can delete complaints."""
        if not (self.request.user.groups.filter(name='admin').exists() or 
                self.request.user.is_superuser):
            return Response(
                {'error': 'Only administrators can delete complaints.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        logger.warning(
            f"Complaint {instance.id} deleted by admin {self.request.user.username}"
        )
        instance.delete()


class ComplaintAssignView(APIView):
    """
    Assign an agent to a complaint.
    Only administrators can perform this action.
    """
    permission_classes = [IsAuthenticated, CanAssignComplaint]
    serializer_class = ComplaintAssignSerializer
    
    def post(self, request, pk):
        """Assign an agent to a complaint."""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            complaint = ComplaintService.assign_agent_to_complaint(
                pk, 
                serializer.validated_data['agent_id']
            )
            
            response_serializer = ComplaintDetailSerializer(complaint)
            return Response({
                'message': 'Agent assigned successfully.',
                'complaint': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except ComplaintNotFoundError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except AgentNotFoundError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except ComplaintServiceError as e:
            logger.error(f"Error assigning agent: {str(e)}")
            return Response(
                {'error': 'An error occurred while assigning the agent.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ComplaintStatusUpdateView(APIView):
    """
    Update the status of a complaint.
    Only admin, assigned agent, or complaint owner can update status.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrAgent]
    serializer_class = ComplaintStatusUpdateSerializer
    
    def patch(self, request, pk):
        """Update complaint status."""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            complaint = ComplaintService.update_complaint_status(
                pk,
                serializer.validated_data['status'],
                request.user
            )
            
            response_serializer = ComplaintDetailSerializer(complaint)
            return Response({
                'message': 'Status updated successfully.',
                'complaint': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except ComplaintNotFoundError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ComplaintServiceError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class DashboardView(APIView):
    """
    Get dashboard analytics data.
    Only accessible to administrators.
    """
    permission_classes = [IsAuthenticated, CanViewDashboard]
    serializer_class = DashboardAnalyticsSerializer
    
    def get(self, request):
        """Get comprehensive dashboard analytics."""
        try:
            analytics_data = DashboardService.get_dashboard_analytics()
            serializer = self.serializer_class(analytics_data)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ComplaintServiceError as e:
            logger.error(f"Error generating dashboard analytics: {str(e)}")
            return Response(
                {'error': 'An error occurred while generating analytics.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MyComplaintsView(generics.ListAPIView):
    """
    List complaints created by the authenticated user.
    """
    serializer_class = ComplaintListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ComplaintService.get_user_complaints(self.request.user)


class AgentComplaintsView(generics.ListAPIView):
    """
    List complaints assigned to the authenticated agent.
    """
    serializer_class = ComplaintListSerializer
    permission_classes = [IsAuthenticated, IsAgentUser]
    
    def get_queryset(self):
        return ComplaintService.get_agent_complaints(self.request.user)


class AvailableAgentsView(APIView):
    """
    Get list of available agents for assignment.
    Only accessible to administrators.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Get list of agents available for assignment."""
        agents = User.objects.filter(
            groups__name='agent', 
            is_active=True
        ).values('id', 'username', 'first_name', 'last_name', 'email')
        
        return Response({
            'agents': list(agents)
        }, status=status.HTTP_200_OK)