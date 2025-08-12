from django.contrib import admin
from .models import (
    CommunicationChannel, Contact, Conversation, Message, 
    InteractionHistory, ChannelIntegration, ConversationTag, 
    ConversationTagAssignment
)


@admin.register(CommunicationChannel)
class CommunicationChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel_type', 'is_active', 'created_at')
    list_filter = ('channel_type', 'is_active', 'created_at')
    search_fields = ('name', 'channel_type')
    ordering = ('-created_at',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'primary_identifier', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone', 'document')
    ordering = ('-created_at',)
    readonly_fields = ('primary_identifier',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('message_id', 'created_at', 'sender_type', 'sender_name')
    fields = ('sender_type', 'sender_name', 'message_type', 'content', 'is_read', 'created_at')


class ConversationTagAssignmentInline(admin.TabularInline):
    model = ConversationTagAssignment
    extra = 0
    readonly_fields = ('assigned_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        'conversation_id', 'contact', 'channel', 'agent', 
        'status', 'priority', 'created_at', 'last_activity'
    )
    list_filter = ('status', 'priority', 'channel__channel_type', 'created_at', 'last_activity')
    search_fields = (
        'conversation_id', 'contact__name', 'contact__email', 
        'agent__username', 'subject'
    )
    ordering = ('-last_activity',)
    readonly_fields = ('conversation_id', 'created_at', 'updated_at', 'last_activity')
    inlines = [MessageInline, ConversationTagAssignmentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'contact', 'channel', 'agent', 'complaint'
        )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'message_id', 'conversation', 'sender_type', 'sender_name', 
        'message_type', 'is_read', 'created_at'
    )
    list_filter = (
        'sender_type', 'message_type', 'is_read', 
        'is_delivered', 'created_at'
    )
    search_fields = (
        'conversation__conversation_id', 'sender_name', 'content'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'message_id', 'created_at', 'updated_at', 
        'delivered_at', 'read_at'
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'conversation', 'sender_user'
        )


@admin.register(InteractionHistory)
class InteractionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'contact', 'interaction_type', 'agent', 
        'channel', 'created_at'
    )
    list_filter = (
        'interaction_type', 'channel__channel_type', 
        'created_at'
    )
    search_fields = (
        'contact__name', 'contact__email', 'agent__username', 
        'description'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'contact', 'agent', 'channel', 'complaint', 'conversation'
        )


@admin.register(ChannelIntegration)
class ChannelIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        'channel', 'sync_status', 'is_connected', 
        'last_sync', 'created_at'
    )
    list_filter = ('sync_status', 'is_connected', 'created_at', 'last_sync')
    search_fields = ('channel__name',)
    ordering = ('-created_at',)
    readonly_fields = (
        'is_connected', 'last_sync', 'sync_status', 
        'error_message', 'created_at', 'updated_at'
    )
    
    # Ocultar campos sensibles
    exclude = ('api_key', 'api_secret', 'webhook_secret', 'email_password')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('channel')


@admin.register(ConversationTag)
class ConversationTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(ConversationTagAssignment)
class ConversationTagAssignmentAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'tag', 'assigned_by', 'assigned_at')
    list_filter = ('tag', 'assigned_at')
    search_fields = (
        'conversation__conversation_id', 'tag__name', 
        'assigned_by__username'
    )
    ordering = ('-assigned_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'conversation', 'tag', 'assigned_by'
        )
