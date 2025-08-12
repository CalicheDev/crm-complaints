from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import timedelta

from .models import (
    CommunicationChannel, Contact, Conversation, Message, 
    InteractionHistory, ChannelIntegration, ConversationTag, 
    ConversationTagAssignment
)
from .serializers import (
    CommunicationChannelSerializer, ContactSerializer, ConversationListSerializer,
    ConversationDetailSerializer, MessageSerializer, InteractionHistorySerializer,
    ChannelIntegrationSerializer, ConversationTagSerializer, ConversationCreateSerializer,
    ContactInteractionSummarySerializer, ConversationTagAssignmentSerializer
)
from complaints.permissions import IsAgentUser, IsAdminUser
from complaints.models import Complaint


class CommunicationChannelViewSet(viewsets.ModelViewSet):
    queryset = CommunicationChannel.objects.all()
    serializer_class = CommunicationChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.filter(name='admin').exists():
            return queryset
        return queryset.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_channels = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_channels, many=True)
        return Response(serializer.data)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(document__icontains=search)
            )
        return queryset

    @action(detail=True, methods=['get'], serializer_class=ContactInteractionSummarySerializer)
    def interaction_summary(self, request, pk=None):
        contact = self.get_object()
        serializer = ContactInteractionSummarySerializer(contact)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def conversations(self, request, pk=None):
        contact = self.get_object()
        conversations = contact.conversations.select_related(
            'channel', 'agent', 'complaint'
        ).prefetch_related('messages', 'tags__tag')
        
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.select_related(
        'contact', 'channel', 'agent', 'complaint'
    ).prefetch_related('messages', 'tags__tag')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtrar por rol del usuario
        if user.groups.filter(name='agent').exists() and not user.groups.filter(name='admin').exists():
            queryset = queryset.filter(agent=user)
        
        # Filtros adicionales
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        channel_filter = self.request.query_params.get('channel', None)
        if channel_filter:
            queryset = queryset.filter(channel_id=channel_filter)
            
        priority_filter = self.request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
            
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(contact__name__icontains=search) |
                Q(contact__email__icontains=search) |
                Q(subject__icontains=search) |
                Q(messages__content__icontains=search)
            ).distinct()

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAgentUser])
    def assign_agent(self, request, pk=None):
        conversation = self.get_object()
        agent_id = request.data.get('agent_id')
        
        if not agent_id:
            return Response(
                {'error': 'agent_id es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            agent = User.objects.get(id=agent_id, groups__name='agent')
            conversation.agent = agent
            conversation.save()
            
            # Crear registro de historial
            InteractionHistory.objects.create(
                contact=conversation.contact,
                conversation=conversation,
                interaction_type='agent_assigned',
                description=f'Conversación asignada al agente {agent.get_full_name() or agent.username}',
                agent=request.user,
                channel=conversation.channel
            )
            
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Agente no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        conversation = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Conversation.CONVERSATION_STATUS):
            return Response(
                {'error': 'Estado inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = conversation.status
        conversation.status = new_status
        conversation.save()
        
        # Crear registro de historial
        InteractionHistory.objects.create(
            contact=conversation.contact,
            conversation=conversation,
            interaction_type='status_changed',
            description=f'Estado cambiado de {old_status} a {new_status}',
            agent=request.user,
            channel=conversation.channel
        )
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.select_related('sender_user').order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        
        # Verificar que el usuario pueda enviar mensajes en esta conversación
        if not request.user.groups.filter(name__in=['admin', 'agent']).exists():
            if conversation.contact.user != request.user:
                return Response(
                    {'error': 'No tienes permisos para enviar mensajes en esta conversación'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        message_data = request.data.copy()
        message_data['conversation'] = conversation.id
        
        # Establecer el tipo de remitente
        if request.user.groups.filter(name__in=['admin', 'agent']).exists():
            message_data['sender_type'] = 'agent'
        else:
            message_data['sender_type'] = 'contact'
        
        serializer = MessageSerializer(data=message_data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            
            # Crear registro de historial
            InteractionHistory.objects.create(
                contact=conversation.contact,
                conversation=conversation,
                interaction_type='message_sent',
                description=f'Mensaje enviado: {message.content[:100]}...' if message.content else f'Archivo enviado: {message.attachment_name}',
                agent=request.user if message.sender_type == 'agent' else None,
                channel=conversation.channel
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        conversation = self.get_object()
        tag_id = request.data.get('tag_id')
        
        try:
            tag = ConversationTag.objects.get(id=tag_id)
            tag_assignment, created = ConversationTagAssignment.objects.get_or_create(
                conversation=conversation,
                tag=tag,
                defaults={'assigned_by': request.user}
            )
            
            if created:
                serializer = ConversationTagAssignmentSerializer(tag_assignment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': 'Tag ya está asignado a esta conversación'}, 
                    status=status.HTTP_200_OK
                )
                
        except ConversationTag.DoesNotExist:
            return Response(
                {'error': 'Tag no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        user = request.user
        queryset = self.get_queryset()
        
        # Estadísticas generales
        total_conversations = queryset.count()
        active_conversations = queryset.filter(status__in=['active', 'waiting']).count()
        resolved_conversations = queryset.filter(status='resolved').count()
        
        # Conversaciones por canal
        conversations_by_channel = list(
            queryset.values('channel__name', 'channel__channel_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Conversaciones por prioridad
        conversations_by_priority = list(
            queryset.values('priority')
            .annotate(count=Count('id'))
        )
        
        # Actividad reciente (últimas 24 horas)
        recent_activity = queryset.filter(
            last_activity__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        return Response({
            'total_conversations': total_conversations,
            'active_conversations': active_conversations,
            'resolved_conversations': resolved_conversations,
            'conversations_by_channel': conversations_by_channel,
            'conversations_by_priority': conversations_by_priority,
            'recent_activity': recent_activity,
        })


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related('conversation', 'sender_user')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        conversation_id = self.request.query_params.get('conversation', None)
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        return queryset.order_by('created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)


class InteractionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InteractionHistory.objects.select_related(
        'contact', 'agent', 'channel', 'complaint', 'conversation'
    )
    serializer_class = InteractionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        contact_id = self.request.query_params.get('contact', None)
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
            
        complaint_id = self.request.query_params.get('complaint', None)
        if complaint_id:
            queryset = queryset.filter(complaint_id=complaint_id)
            
        conversation_id = self.request.query_params.get('conversation', None)
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
            
        return queryset.order_by('-created_at')


class ConversationTagViewSet(viewsets.ModelViewSet):
    queryset = ConversationTag.objects.all()
    serializer_class = ConversationTagSerializer
    permission_classes = [IsAgentUser]

    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_tags = self.queryset.annotate(
            usage_count=Count('conversationtagassignment')
        ).filter(usage_count__gt=0).order_by('-usage_count')[:10]
        
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)


class ChannelIntegrationViewSet(viewsets.ModelViewSet):
    queryset = ChannelIntegration.objects.select_related('channel')
    serializer_class = ChannelIntegrationSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        integration = self.get_object()
        
        # Aquí implementarías la lógica específica para probar cada tipo de canal
        try:
            # Por ahora, simplemente marcamos como conectado
            integration.is_connected = True
            integration.sync_status = 'connected'
            integration.last_sync = timezone.now()
            integration.error_message = None
            integration.save()
            
            return Response({
                'status': 'success',
                'message': f'Conexión exitosa con {integration.channel.name}'
            })
            
        except Exception as e:
            integration.is_connected = False
            integration.sync_status = 'error'
            integration.error_message = str(e)
            integration.save()
            
            return Response({
                'status': 'error',
                'message': f'Error al conectar con {integration.channel.name}: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
