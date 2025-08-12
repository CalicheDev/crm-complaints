from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from complaints.models import Complaint
import uuid


class CommunicationChannel(models.Model):
    CHANNEL_TYPES = [
        ('chat', 'Chat en Vivo'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('phone', 'Llamada Telefónica'),
        ('sms', 'SMS'),
    ]
    
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True, help_text="Configuración específica del canal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'channel_type')

    def __str__(self):
        return f"{self.name} ({self.get_channel_type_display()})"


class Contact(models.Model):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200)
    document = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='contact_profile')
    
    # Canales adicionales
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    facebook_id = models.CharField(max_length=100, blank=True, null=True)
    twitter_handle = models.CharField(max_length=100, blank=True, null=True)
    instagram_handle = models.CharField(max_length=100, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def primary_identifier(self):
        return self.email or self.phone or self.whatsapp_number


class Conversation(models.Model):
    CONVERSATION_STATUS = [
        ('active', 'Activa'),
        ('waiting', 'Esperando Cliente'),
        ('resolved', 'Resuelta'),
        ('closed', 'Cerrada'),
    ]

    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='conversations')
    channel = models.ForeignKey(CommunicationChannel, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_conversations')
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=True, blank=True, related_name='conversations')
    
    subject = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=CONVERSATION_STATUS, default='active')
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ], default='medium')
    
    # Metadatos del canal
    channel_thread_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID del hilo en el canal específico")
    channel_metadata = models.JSONField(default=dict, blank=True, help_text="Metadatos específicos del canal")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.contact.name} - {self.channel.name} ({self.conversation_id})"

    @property
    def is_active(self):
        return self.status in ['active', 'waiting']


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Texto'),
        ('image', 'Imagen'),
        ('file', 'Archivo'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('location', 'Ubicación'),
        ('system', 'Sistema'),
    ]

    SENDER_TYPES = [
        ('contact', 'Contacto'),
        ('agent', 'Agente'),
        ('system', 'Sistema'),
        ('bot', 'Bot'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_id = models.UUIDField(default=uuid.uuid4, editable=False)
    
    sender_type = models.CharField(max_length=20, choices=SENDER_TYPES)
    sender_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=200, blank=True, null=True)
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(blank=True, null=True)
    
    # Para archivos adjuntos
    attachment = models.FileField(upload_to='omnichannel/attachments/', blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True, null=True)
    attachment_size = models.PositiveIntegerField(null=True, blank=True)
    attachment_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadatos del mensaje
    channel_message_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID del mensaje en el canal específico")
    metadata = models.JSONField(default=dict, blank=True)
    
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = self.content[:50] + "..." if self.content and len(self.content) > 50 else self.content
        return f"{self.sender_name or 'Unknown'}: {preview or f'[{self.message_type}]'}"

    def save(self, *args, **kwargs):
        # Actualizar la última actividad de la conversación
        super().save(*args, **kwargs)
        self.conversation.last_activity = self.created_at
        self.conversation.save(update_fields=['last_activity'])


class InteractionHistory(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='interaction_history')
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=True, blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True)
    
    # Relación genérica para poder relacionar con cualquier modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    interaction_type = models.CharField(max_length=50, choices=[
        ('complaint_created', 'PQRS Creada'),
        ('conversation_started', 'Conversación Iniciada'),
        ('message_sent', 'Mensaje Enviado'),
        ('call_made', 'Llamada Realizada'),
        ('email_sent', 'Email Enviado'),
        ('status_changed', 'Estado Cambiado'),
        ('agent_assigned', 'Agente Asignado'),
        ('resolution_provided', 'Solución Proporcionada'),
        ('follow_up', 'Seguimiento'),
        ('other', 'Otro'),
    ])
    
    description = models.TextField()
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.ForeignKey(CommunicationChannel, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contact.name} - {self.get_interaction_type_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class ChannelIntegration(models.Model):
    channel = models.OneToOneField(CommunicationChannel, on_delete=models.CASCADE)
    
    # Configuraciones específicas por canal
    api_key = models.CharField(max_length=500, blank=True, null=True)
    api_secret = models.CharField(max_length=500, blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    
    # Para WhatsApp Business API
    phone_number_id = models.CharField(max_length=100, blank=True, null=True)
    business_account_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Para redes sociales
    page_id = models.CharField(max_length=100, blank=True, null=True)
    app_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Para email
    smtp_server = models.CharField(max_length=200, blank=True, null=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    email_username = models.CharField(max_length=200, blank=True, null=True)
    email_password = models.CharField(max_length=200, blank=True, null=True)
    use_tls = models.BooleanField(default=True)
    
    # Estados y configuraciones
    is_connected = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pendiente'),
        ('connected', 'Conectado'),
        ('error', 'Error'),
        ('disconnected', 'Desconectado'),
    ])
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Integración {self.channel.name}"


class ConversationTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Color en formato hexadecimal")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ConversationTagAssignment(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(ConversationTag, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('conversation', 'tag')
