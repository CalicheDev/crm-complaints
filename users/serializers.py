from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with proper validation."""
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate username."""
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """Create user with validated data."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate login credentials."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile management."""
    groups = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'date_joined', 'last_login', 'is_active', 'groups'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login', 'groups']
    
    def validate_email(self, value):
        """Validate email uniqueness excluding current user."""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    current_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(style={'input_type': 'password'})
    confirm_password = serializers.CharField(style={'input_type': 'password'})
    
    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength."""
        try:
            validate_password(value, self.context['request'].user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (admin view)."""
    groups = serializers.StringRelatedField(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'is_active', 'date_joined', 'last_login', 'groups'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return f"{obj.first_name} {obj.last_name}".strip()


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating user roles."""
    role = serializers.ChoiceField(
        choices=[('admin', 'Administrator'), ('agent', 'Agent'), ('user', 'Regular User')]
    )
    
    def validate_role(self, value):
        """Validate that the role exists."""
        if value != 'user':  # 'user' means no special group
            try:
                Group.objects.get(name=value)
            except Group.DoesNotExist:
                raise serializers.ValidationError(f"Role '{value}' does not exist.")
        return value


class TokenSerializer(serializers.Serializer):
    """Serializer for token response."""
    token = serializers.CharField()
    user = UserProfileSerializer(read_only=True)