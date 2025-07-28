from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Complaint


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with limited fields for security."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ComplaintListSerializer(serializers.ModelSerializer):
    """Serializer for listing complaints with minimal fields."""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = Complaint
        fields = [
            'id', 'title', 'status', 'created_at', 
            'updated_at', 'created_by', 'assigned_to'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComplaintDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed complaint view with all fields."""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def validate_title(self, value):
        """Validate complaint title."""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )
        if len(value) > 255:
            raise serializers.ValidationError(
                "Title cannot exceed 255 characters."
            )
        return value.strip()
    
    def validate_description(self, value):
        """Validate complaint description."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Description must be at least 10 characters long."
            )
        if len(value) > 2000:
            raise serializers.ValidationError(
                "Description cannot exceed 2000 characters."
            )
        return value.strip()
    
    def validate_status(self, value):
        """Validate complaint status."""
        valid_statuses = ['pending', 'in_progress', 'resolved']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new complaints."""
    
    class Meta:
        model = Complaint
        fields = ['title', 'description']
    
    def validate_title(self, value):
        """Validate complaint title."""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )
        if len(value) > 255:
            raise serializers.ValidationError(
                "Title cannot exceed 255 characters."
            )
        return value.strip()
    
    def validate_description(self, value):
        """Validate complaint description."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Description must be at least 10 characters long."
            )
        if len(value) > 2000:
            raise serializers.ValidationError(
                "Description cannot exceed 2000 characters."
            )
        return value.strip()


class ComplaintAssignSerializer(serializers.Serializer):
    """Serializer for assigning agents to complaints."""
    agent_id = serializers.IntegerField(min_value=1)
    
    def validate_agent_id(self, value):
        """Validate that the agent exists and has the correct role."""
        try:
            agent = User.objects.get(pk=value, groups__name='agent')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Agent not found or user does not have agent role."
            )


class ComplaintStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating complaint status."""
    status = serializers.ChoiceField(
        choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')]
    )


class DashboardAnalyticsSerializer(serializers.Serializer):
    """Serializer for dashboard analytics data."""
    total_complaints = serializers.IntegerField()
    complaints_by_status = serializers.ListField()
    avg_resolution_time = serializers.FloatField(allow_null=True)
    agents_load = serializers.ListField()
    recent_complaints = serializers.ListField()
    monthly_trends = serializers.ListField()