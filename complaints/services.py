import logging
from typing import Dict, List, Optional, Any
from django.contrib.auth.models import User
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField, Q
from django.utils.timezone import now
from datetime import timedelta
from .models import Complaint
from .exceptions import ComplaintServiceError, AgentNotFoundError, ComplaintNotFoundError


logger = logging.getLogger(__name__)


class ComplaintService:
    """
    Service class to handle complaint-related business logic.
    Follows Single Responsibility Principle - only handles complaint operations.
    """
    
    @staticmethod
    def create_complaint(data: Dict[str, Any], user: Optional[User] = None) -> Complaint:
        """
        Create a new complaint.
        
        Args:
            data: Complaint data
            user: User creating the complaint (can be None for anonymous complaints)
            
        Returns:
            Created complaint instance
            
        Raises:
            ComplaintServiceError: If creation fails
        """
        try:
            complaint_data = {
                'title': data.get('title'),
                'description': data.get('description'),
                'status': 'pending'
            }
            
            if user and user.is_authenticated:
                complaint_data['created_by'] = user
                
            complaint = Complaint.objects.create(**complaint_data)
            logger.info(f"Complaint created with ID: {complaint.id}")
            return complaint
            
        except Exception as e:
            logger.error(f"Error creating complaint: {str(e)}")
            raise ComplaintServiceError(f"Error creating complaint: {str(e)}")
    
    @staticmethod
    def assign_agent_to_complaint(complaint_id: int, agent_id: int) -> Complaint:
        """
        Assign an agent to a complaint.
        
        Args:
            complaint_id: ID of the complaint
            agent_id: ID of the agent
            
        Returns:
            Updated complaint instance
            
        Raises:
            ComplaintNotFoundError: If complaint doesn't exist
            AgentNotFoundError: If agent doesn't exist or isn't valid
        """
        try:
            complaint = Complaint.objects.get(pk=complaint_id)
        except Complaint.DoesNotExist:
            raise ComplaintNotFoundError(f"Complaint with ID {complaint_id} not found")
        
        try:
            agent = User.objects.get(pk=agent_id, groups__name='agent')
        except User.DoesNotExist:
            raise AgentNotFoundError(f"Agent with ID {agent_id} not found or invalid")
        
        complaint.assigned_to = agent
        complaint.status = 'in_progress'
        complaint.save()
        
        logger.info(f"Agent {agent.username} assigned to complaint {complaint_id}")
        return complaint
    
    @staticmethod
    def get_user_complaints(user: User) -> List[Complaint]:
        """
        Get complaints created by a specific user.
        
        Args:
            user: User instance
            
        Returns:
            List of complaints created by the user
        """
        return Complaint.objects.filter(created_by=user).order_by('-created_at')
    
    @staticmethod
    def get_agent_complaints(agent: User) -> List[Complaint]:
        """
        Get complaints assigned to a specific agent.
        
        Args:
            agent: Agent user instance
            
        Returns:
            List of complaints assigned to the agent
        """
        return Complaint.objects.filter(assigned_to=agent).order_by('-created_at')
    
    @staticmethod
    def update_complaint_status(complaint_id: int, new_status: str, user: User) -> Complaint:
        """
        Update complaint status.
        
        Args:
            complaint_id: ID of the complaint
            new_status: New status value
            user: User making the update
            
        Returns:
            Updated complaint instance
            
        Raises:
            ComplaintNotFoundError: If complaint doesn't exist
            ComplaintServiceError: If update fails
        """
        try:
            complaint = Complaint.objects.get(pk=complaint_id)
        except Complaint.DoesNotExist:
            raise ComplaintNotFoundError(f"Complaint with ID {complaint_id} not found")
        
        # Validate status
        valid_statuses = ['pending', 'in_progress', 'resolved']
        if new_status not in valid_statuses:
            raise ComplaintServiceError(f"Invalid status: {new_status}")
        
        complaint.status = new_status
        complaint.save()
        
        logger.info(f"Complaint {complaint_id} status updated to {new_status} by {user.username}")
        return complaint


class DashboardService:
    """
    Service class to handle dashboard analytics.
    Follows Single Responsibility Principle - only handles dashboard data.
    """
    
    @staticmethod
    def get_dashboard_analytics() -> Dict[str, Any]:
        """
        Get comprehensive dashboard analytics.
        
        Returns:
            Dictionary containing all dashboard metrics
        """
        try:
            analytics = {
                'total_complaints': DashboardService._get_total_complaints(),
                'complaints_by_status': DashboardService._get_complaints_by_status(),
                'avg_resolution_time': DashboardService._get_avg_resolution_time(),
                'agents_load': DashboardService._get_agents_load(),
                'recent_complaints': DashboardService._get_recent_complaints(),
                'monthly_trends': DashboardService._get_monthly_trends(),
            }
            
            logger.info("Dashboard analytics generated successfully")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating dashboard analytics: {str(e)}")
            raise ComplaintServiceError(f"Error generating dashboard analytics: {str(e)}")
    
    @staticmethod
    def _get_total_complaints() -> int:
        """Get total number of complaints."""
        return Complaint.objects.count()
    
    @staticmethod
    def _get_complaints_by_status() -> List[Dict[str, Any]]:
        """Get complaints count grouped by status."""
        return list(
            Complaint.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
    
    @staticmethod
    def _get_avg_resolution_time() -> Optional[float]:
        """Get average resolution time for resolved complaints."""
        result = Complaint.objects.filter(status='resolved').annotate(
            resolution_time=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(avg_time=Avg('resolution_time'))
        
        return result['avg_time'].total_seconds() if result['avg_time'] else None
    
    @staticmethod
    def _get_agents_load() -> List[Dict[str, Any]]:
        """Get current workload for each agent."""
        return list(
            Complaint.objects.filter(assigned_to__groups__name='agent')
            .values('assigned_to__username', 'assigned_to__first_name', 'assigned_to__last_name')
            .annotate(
                active_complaints=Count('id', filter=Q(status__in=['pending', 'in_progress'])),
                total_complaints=Count('id'),
                resolved_complaints=Count('id', filter=Q(status='resolved'))
            )
            .order_by('-active_complaints')
        )
    
    @staticmethod
    def _get_recent_complaints(limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent complaints for quick overview."""
        return list(
            Complaint.objects.select_related('created_by', 'assigned_to')
            .order_by('-created_at')[:limit]
            .values(
                'id', 'title', 'status', 'created_at',
                'created_by__username', 'assigned_to__username'
            )
        )
    
    @staticmethod
    def _get_monthly_trends() -> List[Dict[str, Any]]:
        """Get monthly complaint trends for the last 12 months."""
        from django.db.models import DateTrunc
        
        return list(
            Complaint.objects.annotate(
                month=DateTrunc('month', 'created_at')
            ).values('month')
            .annotate(
                total=Count('id'),
                resolved=Count('id', filter=Q(status='resolved')),
                pending=Count('id', filter=Q(status='pending')),
                in_progress=Count('id', filter=Q(status='in_progress'))
            )
            .order_by('-month')[:12]
        )