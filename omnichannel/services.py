from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import json
import requests
import logging

from .models import (
    CommunicationChannel, Contact, Conversation, Message, 
    InteractionHistory, ChannelIntegration
)

logger = logging.getLogger(__name__)


class ChannelHandler(ABC):
    """Clase base abstracta para manejadores de canales de comunicación"""
    
    def __init__(self, channel: CommunicationChannel):
        self.channel = channel
        self.integration = getattr(channel, 'channelintegration', None)
    
    @abstractmethod
    def send_message(self, conversation: Conversation, content: str, **kwargs) -> bool:
        """Envía un mensaje a través del canal específico"""
        pass
    
    @abstractmethod
    def validate_configuration(self) -> Dict[str, Any]:
        """Valida la configuración del canal"""
        pass
    
    def create_interaction_history(self, contact: Contact, conversation: Conversation, 
                                 description: str, agent=None, metadata=None):
        """Crea un registro en el historial de interacciones"""
        InteractionHistory.objects.create(
            contact=contact,
            conversation=conversation,
            interaction_type='message_sent',
            description=description,
            agent=agent,
            channel=self.channel,
            metadata=metadata or {}
        )


class EmailChannelHandler(ChannelHandler):
    """Manejador para el canal de email"""
    
    def send_message(self, conversation: Conversation, content: str, 
                    subject: str = None, **kwargs) -> bool:
        try:
            if not self.integration:
                logger.error("No hay integración configurada para el canal de email")
                return False
            
            recipient_email = conversation.contact.email
            if not recipient_email:
                logger.error("El contacto no tiene email configurado")
                return False
            
            email_subject = subject or f"Respuesta a su solicitud - {conversation.subject or 'Sin asunto'}"
            
            # Configurar el email
            from_email = self.integration.email_username
            
            send_mail(
                subject=email_subject,
                message=content,
                from_email=from_email,
                recipient_list=[recipient_email],
                fail_silently=False
            )
            
            logger.info(f"Email enviado exitosamente a {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        if not self.integration:
            return {'valid': False, 'errors': ['No hay integración configurada']}
        
        errors = []
        if not self.integration.smtp_server:
            errors.append('Servidor SMTP no configurado')
        if not self.integration.smtp_port:
            errors.append('Puerto SMTP no configurado')
        if not self.integration.email_username:
            errors.append('Usuario de email no configurado')
        if not self.integration.email_password:
            errors.append('Contraseña de email no configurada')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class WhatsAppChannelHandler(ChannelHandler):
    """Manejador para el canal de WhatsApp Business API"""
    
    def send_message(self, conversation: Conversation, content: str, **kwargs) -> bool:
        try:
            if not self.integration:
                logger.error("No hay integración configurada para WhatsApp")
                return False
            
            phone_number = conversation.contact.whatsapp_number or conversation.contact.phone
            if not phone_number:
                logger.error("El contacto no tiene número de WhatsApp configurado")
                return False
            
            # Limpiar el número de teléfono
            clean_phone = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # URL de la API de WhatsApp Business
            url = f"https://graph.facebook.com/v17.0/{self.integration.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.integration.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': clean_phone,
                'type': 'text',
                'text': {'body': content}
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Mensaje de WhatsApp enviado exitosamente a {phone_number}")
                return True
            else:
                logger.error(f"Error enviando mensaje de WhatsApp: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando mensaje de WhatsApp: {str(e)}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        if not self.integration:
            return {'valid': False, 'errors': ['No hay integración configurada']}
        
        errors = []
        if not self.integration.api_key:
            errors.append('Token de acceso no configurado')
        if not self.integration.phone_number_id:
            errors.append('ID del número de teléfono no configurado')
        if not self.integration.business_account_id:
            errors.append('ID de cuenta de negocio no configurado')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class FacebookChannelHandler(ChannelHandler):
    """Manejador para el canal de Facebook Messenger"""
    
    def send_message(self, conversation: Conversation, content: str, **kwargs) -> bool:
        try:
            if not self.integration:
                logger.error("No hay integración configurada para Facebook")
                return False
            
            facebook_id = conversation.contact.facebook_id
            if not facebook_id:
                logger.error("El contacto no tiene Facebook ID configurado")
                return False
            
            url = f"https://graph.facebook.com/v17.0/me/messages"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'recipient': {'id': facebook_id},
                'message': {'text': content},
                'access_token': self.integration.api_key
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Mensaje de Facebook enviado exitosamente a {facebook_id}")
                return True
            else:
                logger.error(f"Error enviando mensaje de Facebook: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando mensaje de Facebook: {str(e)}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        if not self.integration:
            return {'valid': False, 'errors': ['No hay integración configurada']}
        
        errors = []
        if not self.integration.api_key:
            errors.append('Token de página no configurado')
        if not self.integration.page_id:
            errors.append('ID de página no configurado')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class PhoneChannelHandler(ChannelHandler):
    """Manejador para llamadas telefónicas (registro de actividad)"""
    
    def send_message(self, conversation: Conversation, content: str, 
                    call_duration: int = None, call_result: str = None, **kwargs) -> bool:
        """Para llamadas, registra la actividad en lugar de 'enviar'"""
        try:
            # Crear un mensaje del sistema que registre la llamada
            Message.objects.create(
                conversation=conversation,
                sender_type='system',
                sender_name='Sistema de Llamadas',
                message_type='system',
                content=content,
                metadata={
                    'call_duration': call_duration,
                    'call_result': call_result,
                    'phone_number': conversation.contact.phone
                }
            )
            
            # Crear registro en el historial
            self.create_interaction_history(
                contact=conversation.contact,
                conversation=conversation,
                description=f"Llamada realizada: {content}",
                metadata={
                    'call_duration': call_duration,
                    'call_result': call_result
                }
            )
            
            logger.info(f"Llamada registrada para {conversation.contact.phone}")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando llamada: {str(e)}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        # Las llamadas no requieren configuración especial de API
        return {'valid': True, 'errors': []}


class ChatChannelHandler(ChannelHandler):
    """Manejador para chat en vivo (WebSocket o similar)"""
    
    def send_message(self, conversation: Conversation, content: str, **kwargs) -> bool:
        """Para chat en vivo, el mensaje se maneja internamente"""
        try:
            # En un sistema real, aquí enviarías el mensaje via WebSocket
            # Por ahora, solo registramos que el mensaje fue "enviado"
            
            logger.info(f"Mensaje de chat enviado en conversación {conversation.conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando mensaje de chat: {str(e)}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        # El chat en vivo funciona internamente, no requiere configuración externa
        return {'valid': True, 'errors': []}


class ChannelService:
    """Servicio principal para manejo de canales de comunicación"""
    
    CHANNEL_HANDLERS = {
        'email': EmailChannelHandler,
        'whatsapp': WhatsAppChannelHandler,
        'facebook': FacebookChannelHandler,
        'phone': PhoneChannelHandler,
        'chat': ChatChannelHandler,
    }
    
    @classmethod
    def get_handler(cls, channel: CommunicationChannel) -> Optional[ChannelHandler]:
        """Obtiene el manejador apropiado para un canal"""
        handler_class = cls.CHANNEL_HANDLERS.get(channel.channel_type)
        if handler_class:
            return handler_class(channel)
        return None
    
    @classmethod
    def send_message_via_channel(cls, conversation: Conversation, content: str, 
                               sender_user=None, **kwargs) -> Dict[str, Any]:
        """Envía un mensaje a través del canal apropiado"""
        try:
            handler = cls.get_handler(conversation.channel)
            if not handler:
                return {
                    'success': False,
                    'error': f'No hay manejador disponible para el canal {conversation.channel.channel_type}'
                }
            
            # Crear el mensaje en la base de datos
            message = Message.objects.create(
                conversation=conversation,
                sender_type='agent' if sender_user else 'system',
                sender_user=sender_user,
                sender_name=sender_user.get_full_name() if sender_user else 'Sistema',
                content=content,
                message_type='text'
            )
            
            # Enviar a través del canal específico
            success = handler.send_message(conversation, content, **kwargs)
            
            if success:
                message.is_delivered = True
                message.delivered_at = timezone.now()
                message.save()
                
                # Crear registro en el historial
                handler.create_interaction_history(
                    contact=conversation.contact,
                    conversation=conversation,
                    description=f'Mensaje enviado vía {conversation.channel.name}: {content[:100]}...',
                    agent=sender_user
                )
                
                return {'success': True, 'message_id': message.id}
            else:
                return {'success': False, 'error': 'Error enviando mensaje a través del canal'}
                
        except Exception as e:
            logger.error(f"Error en send_message_via_channel: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def validate_channel_integration(cls, channel: CommunicationChannel) -> Dict[str, Any]:
        """Valida la configuración de integración de un canal"""
        handler = cls.get_handler(channel)
        if not handler:
            return {
                'valid': False,
                'errors': [f'No hay manejador disponible para {channel.channel_type}']
            }
        
        return handler.validate_configuration()
    
    @classmethod
    def get_available_channels_for_contact(cls, contact: Contact) -> List[CommunicationChannel]:
        """Obtiene los canales disponibles para un contacto específico"""
        available_channels = []
        
        # Verificar qué canales están disponibles según la información del contacto
        channels = CommunicationChannel.objects.filter(is_active=True)
        
        for channel in channels:
            can_use_channel = False
            
            if channel.channel_type == 'email' and contact.email:
                can_use_channel = True
            elif channel.channel_type == 'whatsapp' and (contact.whatsapp_number or contact.phone):
                can_use_channel = True
            elif channel.channel_type == 'phone' and contact.phone:
                can_use_channel = True
            elif channel.channel_type == 'facebook' and contact.facebook_id:
                can_use_channel = True
            elif channel.channel_type == 'chat':
                can_use_channel = True  # El chat siempre está disponible
            
            if can_use_channel:
                available_channels.append(channel)
        
        return available_channels