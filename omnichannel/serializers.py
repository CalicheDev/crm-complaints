from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    CommunicationChannel, Contact, Conversation, Message, 
    InteractionHistory, ChannelIntegration, ConversationTag, 
    ConversationTagAssignment
)
from complaints.serializers import ComplaintListSerializer
from users.serializers import UserListSerializer


class CommunicationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationChannel
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ContactSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    primary_identifier = serializers.ReadOnlyField()

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ConversationTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationTag
        fields = '__all__'
        read_only_fields = ('created_at',)


class ConversationTagAssignmentSerializer(serializers.ModelSerializer):
    tag = ConversationTagSerializer(read_only=True)
    assigned_by = UserListSerializer(read_only=True)

    class Meta:
        model = ConversationTagAssignment
        fields = '__all__'
        read_only_fields = ('assigned_at',)


class MessageSerializer(serializers.ModelSerializer):
    sender_user = UserListSerializer(read_only=True)
    attachment_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = (
            'message_id', 'created_at', 'updated_at', 
            'delivered_at', 'read_at'
        )

    def get_attachment_size_mb(self, obj):
        if obj.attachment_size:
            return round(obj.attachment_size / (1024 * 1024), 2)
        return None

    def create(self, validated_data):
        # Establecer el usuario remitente si está autenticado
        request = self.context.get('request')
        if request and request.user.is_authenticated and validated_data.get('sender_type') == 'agent':
            validated_data['sender_user'] = request.user
            validated_data['sender_name'] = request.user.get_full_name() or request.user.username
        
        return super().create(validated_data)


class ConversationListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)
    channel = CommunicationChannelSerializer(read_only=True)
    agent = UserListSerializer(read_only=True)
    complaint = ComplaintListSerializer(read_only=True)
    tags = ConversationTagAssignmentSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = (
            'conversation_id', 'created_at', 'updated_at', 'last_activity'
        )

    def get_unread_count(self, obj):
        return obj.messages.filter(is_read=False, sender_type='contact').count()

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content,
                'message_type': last_message.message_type,
                'sender_type': last_message.sender_type,
                'sender_name': last_message.sender_name,
                'created_at': last_message.created_at,
            }
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)
    channel = CommunicationChannelSerializer(read_only=True)
    agent = UserListSerializer(read_only=True)
    complaint = ComplaintListSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    tags = ConversationTagAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = (
            'conversation_id', 'created_at', 'updated_at', 'last_activity'
        )


class InteractionHistorySerializer(serializers.ModelSerializer):
    agent = UserListSerializer(read_only=True)
    channel = CommunicationChannelSerializer(read_only=True)
    contact = ContactSerializer(read_only=True)
    complaint = ComplaintListSerializer(read_only=True)
    conversation = ConversationListSerializer(read_only=True)

    class Meta:
        model = InteractionHistory
        fields = '__all__'
        read_only_fields = ('created_at',)


class ChannelIntegrationSerializer(serializers.ModelSerializer):
    channel = CommunicationChannelSerializer(read_only=True)

    class Meta:
        model = ChannelIntegration
        fields = '__all__'
        read_only_fields = (
            'is_connected', 'last_sync', 'sync_status', 'error_message',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'webhook_secret': {'write_only': True},
            'email_password': {'write_only': True},
        }


class ConversationCreateSerializer(serializers.ModelSerializer):
    contact_data = ContactSerializer(write_only=True, required=False)
    contact_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Conversation
        fields = [
            'channel', 'complaint', 'subject', 'priority', 
            'contact_data', 'contact_id', 'channel_thread_id', 'channel_metadata'
        ]

    def validate(self, data):
        if not data.get('contact_data') and not data.get('contact_id'):
            raise serializers.ValidationError(
                "Debe proporcionar contact_data o contact_id"
            )
        return data

    def create(self, validated_data):
        contact_data = validated_data.pop('contact_data', None)
        contact_id = validated_data.pop('contact_id', None)

        if contact_data:
            # Buscar contacto existente o crear uno nuevo
            contact = Contact.objects.filter(
                email=contact_data.get('email')
            ).first() if contact_data.get('email') else None
            
            if not contact and contact_data.get('phone'):
                contact = Contact.objects.filter(
                    phone=contact_data.get('phone')
                ).first()
            
            if not contact:
                contact = Contact.objects.create(**contact_data)
        else:
            contact = Contact.objects.get(id=contact_id)

        validated_data['contact'] = contact
        return super().create(validated_data)


class ContactInteractionSummarySerializer(serializers.ModelSerializer):
    total_conversations = serializers.SerializerMethodField()
    total_complaints = serializers.SerializerMethodField()
    last_interaction = serializers.SerializerMethodField()
    preferred_channels = serializers.SerializerMethodField()
    interaction_history = InteractionHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_total_conversations(self, obj):
        return obj.conversations.count()

    def get_total_complaints(self, obj):
        return obj.conversations.filter(complaint__isnull=False).values('complaint').distinct().count()

    def get_last_interaction(self, obj):
        last_interaction = obj.interaction_history.first()
        if last_interaction:
            return InteractionHistorySerializer(last_interaction).data
        return None

    def get_preferred_channels(self, obj):
        # Obtener los canales más utilizados por el contacto
        channel_usage = {}
        for conversation in obj.conversations.all():
            channel_name = conversation.channel.name
            channel_usage[channel_name] = channel_usage.get(channel_name, 0) + 1
        
        # Ordenar por uso descendente
        sorted_channels = sorted(channel_usage.items(), key=lambda x: x[1], reverse=True)
        return [{'channel': channel, 'usage_count': count} for channel, count in sorted_channels[:3]]