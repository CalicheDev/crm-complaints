import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Complaint, Atencion, ComplaintAttachment
from .serializers import (
    ComplaintListSerializer, ComplaintDetailSerializer, ComplaintCreateSerializer,
    ComplaintAssignSerializer, ComplaintStatusUpdateSerializer, DashboardAnalyticsSerializer,
    AtencionSerializer, AtencionCreateSerializer
)
from .serializers_pqrs import PublicPQRSSerializer
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


class AtencionListCreateView(generics.ListCreateAPIView):
    """
    List atenciones for a specific complaint or create a new atencion.
    Only agents and admins can create atenciones.
    """
    permission_classes = [IsAuthenticated]  # Temporarily relaxed for debugging
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AtencionCreateSerializer
        return AtencionSerializer
    
    def get_queryset(self):
        """Get atenciones for a specific complaint."""
        complaint_id = self.kwargs.get('complaint_id')
        return Atencion.objects.filter(complaint_id=complaint_id).select_related('agent', 'complaint')
    
    def perform_create(self, serializer):
        """Create a new atencion for the complaint."""
        complaint_id = self.kwargs.get('complaint_id')
        
        try:
            complaint = Complaint.objects.get(id=complaint_id)
            
            # Check if the agent is assigned to this complaint or is admin
            user = self.request.user
            
            # Debug logging
            logger.info(f"User {user.username} trying to create atencion for complaint {complaint_id}")
            logger.info(f"Complaint assigned to: {complaint.assigned_to}")
            logger.info(f"User is admin: {user.groups.filter(name='admin').exists()}")
            logger.info(f"User is superuser: {user.is_superuser}")
            logger.info(f"User groups: {[g.name for g in user.groups.all()]}")
            
            # Temporarily allow all authenticated users for debugging
            # TODO: Restore proper permission checking after debugging
            can_create = (
                complaint.assigned_to == user or 
                user.groups.filter(name='admin').exists() or 
                user.groups.filter(name='agent').exists() or
                user.is_superuser
            )
            
            if not can_create:
                from rest_framework.exceptions import PermissionDenied
                error_msg = f'Solo puedes agregar atenciones a quejas asignadas a ti. Queja asignada a: {complaint.assigned_to}, Tu usuario: {user.username}'
                logger.warning(f"Permission denied: {error_msg}")
                raise PermissionDenied(error_msg)
            
            # Save the atencion with the complaint and agent
            atencion = serializer.save(complaint=complaint, agent=user)
            
            logger.info(
                f"Atencion created for complaint {complaint_id} by agent {user.username}"
            )
            
        except Complaint.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Queja no encontrada.')


class AtencionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific atencion.
    Only the agent who created it or admin can modify it.
    """
    serializer_class = AtencionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAgent]
    
    def get_queryset(self):
        return Atencion.objects.select_related('agent', 'complaint')
    
    def get_object(self):
        """Get atencion and check permissions."""
        atencion = super().get_object()
        user = self.request.user
        
        # Check if user can access this atencion
        if not (atencion.agent == user or 
                user.groups.filter(name='admin').exists() or 
                user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permisos para acceder a esta atención.")
        
        return atencion
    
    def perform_update(self, serializer):
        """Update atencion with logging."""
        atencion = serializer.save()
        logger.info(
            f"Atencion {atencion.id} updated by user {self.request.user.username}"
        )
    
    def perform_destroy(self, instance):
        """Delete atencion with proper permissions check."""
        user = self.request.user
        
        # Only the agent who created it or admin can delete
        if not (instance.agent == user or 
                user.groups.filter(name='admin').exists() or 
                user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Solo puedes eliminar tus propias atenciones.')
        
        logger.warning(
            f"Atencion {instance.id} deleted by user {user.username}"
        )
        instance.delete()


class DiagnosticView(APIView):
    """
    Diagnostic view to check user permissions and complaint assignments.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, complaint_id):
        """Get diagnostic information about user permissions."""
        try:
            complaint = Complaint.objects.get(id=complaint_id)
            user = request.user
            
            diagnostic_info = {
                'user_info': {
                    'username': user.username,
                    'is_authenticated': user.is_authenticated,
                    'is_superuser': user.is_superuser,
                    'groups': [g.name for g in user.groups.all()],
                },
                'complaint_info': {
                    'id': complaint.id,
                    'title': complaint.title,
                    'assigned_to': complaint.assigned_to.username if complaint.assigned_to else None,
                },
                'permissions': {
                    'is_admin': user.groups.filter(name='admin').exists(),
                    'is_agent': user.groups.filter(name='agent').exists(),
                    'is_assigned_agent': complaint.assigned_to == user,
                    'can_create_atencion': (
                        complaint.assigned_to == user or 
                        user.groups.filter(name='admin').exists() or 
                        user.is_superuser
                    ),
                }
            }
            
            return Response(diagnostic_info, status=status.HTTP_200_OK)
            
        except Complaint.DoesNotExist:
            return Response(
                {'error': 'Queja no encontrada.'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class PublicPQRSCreateView(APIView):
    """
    Public endpoint for anonymous PQRS submission.
    No authentication required.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = PublicPQRSSerializer
    
    def post(self, request):
        """Create a public PQRS with file attachments."""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Create the complaint
            complaint_data = serializer.validated_data
            files = request.FILES.getlist('attachments', [])
            
            # Create complaint without user
            complaint = Complaint.objects.create(
                title=complaint_data['title'],
                description=complaint_data['description'],
                complaint_type=complaint_data['complaint_type'],
                citizen_name=complaint_data['citizen_name'],
                citizen_email=complaint_data.get('citizen_email'),
                citizen_phone=complaint_data.get('citizen_phone'),
                citizen_address=complaint_data.get('citizen_address'),
                citizen_document=complaint_data.get('citizen_document'),
                created_by=None  # Anonymous submission
            )
            
            # Handle file attachments
            for file in files:
                if file.size > 10 * 1024 * 1024:  # 10MB limit
                    complaint.delete()  # Rollback
                    return Response(
                        {'error': f'File {file.name} exceeds 10MB limit'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check file type
                allowed_types = [
                    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                    'application/pdf', 'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain'
                ]
                
                if file.content_type not in allowed_types:
                    complaint.delete()  # Rollback
                    return Response(
                        {'error': f'File type {file.content_type} not allowed'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                ComplaintAttachment.objects.create(
                    complaint=complaint,
                    file=file,
                    original_filename=file.name,
                    file_size=file.size,
                    content_type=file.content_type
                )
            
            logger.info(
                f"Public PQRS created: {complaint.id} by {complaint.citizen_name} ({complaint.citizen_email})"
            )
            
            return Response({
                'message': 'PQRS enviado exitosamente. Se le asignará un asesor pronto.',
                'complaint_id': complaint.id,
                'complaint_type': complaint.complaint_type,
                'title': complaint.title
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating public PQRS: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor. Intente nuevamente.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )