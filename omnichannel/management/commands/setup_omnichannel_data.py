from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from omnichannel.models import (
    CommunicationChannel, Contact, Conversation, Message, 
    ConversationTag, ChannelIntegration
)
from complaints.models import Complaint


class Command(BaseCommand):
    help = 'Setup initial data for omnichannel functionality'

    def handle(self, *args, **options):
        self.stdout.write('Setting up omnichannel data...')
        
        # Create communication channels
        channels_data = [
            {'name': 'Chat en Vivo', 'channel_type': 'chat'},
            {'name': 'Email Soporte', 'channel_type': 'email'},
            {'name': 'WhatsApp Business', 'channel_type': 'whatsapp'},
            {'name': 'Facebook Messenger', 'channel_type': 'facebook'},
            {'name': 'Twitter DM', 'channel_type': 'twitter'},
            {'name': 'Instagram Direct', 'channel_type': 'instagram'},
            {'name': 'Línea Telefónica', 'channel_type': 'phone'},
            {'name': 'SMS', 'channel_type': 'sms'},
        ]
        
        for channel_data in channels_data:
            channel, created = CommunicationChannel.objects.get_or_create(
                name=channel_data['name'],
                channel_type=channel_data['channel_type']
            )
            if created:
                self.stdout.write(f'Created channel: {channel.name}')
        
        # Create conversation tags
        tags_data = [
            {'name': 'Urgente', 'color': '#dc2626'},
            {'name': 'Consulta', 'color': '#2563eb'},
            {'name': 'Reclamo', 'color': '#ea580c'},
            {'name': 'Información', 'color': '#059669'},
            {'name': 'Seguimiento', 'color': '#7c3aed'},
            {'name': 'Resuelto', 'color': '#16a34a'},
        ]
        
        for tag_data in tags_data:
            tag, created = ConversationTag.objects.get_or_create(
                name=tag_data['name'],
                defaults={'color': tag_data['color']}
            )
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
        
        # Create sample contacts
        contacts_data = [
            {
                'name': 'María García',
                'email': 'maria.garcia@email.com',
                'phone': '+57 300 123 4567',
                'whatsapp_number': '+57 300 123 4567',
                'document': '12345678'
            },
            {
                'name': 'Carlos López',
                'email': 'carlos.lopez@email.com',
                'phone': '+57 301 987 6543',
                'document': '87654321'
            },
            {
                'name': 'Ana Rodríguez',
                'email': 'ana.rodriguez@email.com',
                'phone': '+57 302 456 7890',
                'whatsapp_number': '+57 302 456 7890',
                'facebook_id': 'ana.rodriguez.fb'
            },
        ]
        
        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(
                email=contact_data['email'],
                defaults=contact_data
            )
            if created:
                self.stdout.write(f'Created contact: {contact.name}')
        
        # Create sample conversations and messages
        if CommunicationChannel.objects.exists() and Contact.objects.exists():
            chat_channel = CommunicationChannel.objects.filter(channel_type='chat').first()
            whatsapp_channel = CommunicationChannel.objects.filter(channel_type='whatsapp').first()
            email_channel = CommunicationChannel.objects.filter(channel_type='email').first()
            
            contacts = Contact.objects.all()[:3]
            agents = User.objects.filter(groups__name='agent')
            
            if agents.exists():
                agent = agents.first()
                
                # Conversation 1: Chat conversation
                if chat_channel and len(contacts) > 0:
                    conv1, created = Conversation.objects.get_or_create(
                        contact=contacts[0],
                        channel=chat_channel,
                        defaults={
                            'agent': agent,
                            'subject': 'Consulta sobre servicios',
                            'status': 'active',
                            'priority': 'medium'
                        }
                    )
                    if created:
                        self.stdout.write(f'Created conversation: {conv1.id}')
                        
                        # Add messages
                        Message.objects.create(
                            conversation=conv1,
                            sender_type='contact',
                            sender_name=contacts[0].name,
                            content='Hola, necesito información sobre sus servicios.'
                        )
                        
                        Message.objects.create(
                            conversation=conv1,
                            sender_type='agent',
                            sender_user=agent,
                            sender_name=agent.get_full_name() or agent.username,
                            content='¡Hola! Con gusto le ayudo con información sobre nuestros servicios. ¿Qué tipo de servicio le interesa?'
                        )
                
                # Conversation 2: WhatsApp conversation
                if whatsapp_channel and len(contacts) > 1:
                    conv2, created = Conversation.objects.get_or_create(
                        contact=contacts[1],
                        channel=whatsapp_channel,
                        defaults={
                            'agent': agent,
                            'subject': 'Problema con facturación',
                            'status': 'waiting',
                            'priority': 'high'
                        }
                    )
                    if created:
                        self.stdout.write(f'Created conversation: {conv2.id}')
                        
                        Message.objects.create(
                            conversation=conv2,
                            sender_type='contact',
                            sender_name=contacts[1].name,
                            content='Tengo un problema con mi factura del mes pasado'
                        )
                
                # Conversation 3: Email conversation (resolved)
                if email_channel and len(contacts) > 2:
                    conv3, created = Conversation.objects.get_or_create(
                        contact=contacts[2],
                        channel=email_channel,
                        defaults={
                            'agent': agent,
                            'subject': 'Solicitud de información',
                            'status': 'resolved',
                            'priority': 'low'
                        }
                    )
                    if created:
                        self.stdout.write(f'Created conversation: {conv3.id}')
                        
                        Message.objects.create(
                            conversation=conv3,
                            sender_type='contact',
                            sender_name=contacts[2].name,
                            content='¿Podrían enviarme información sobre los nuevos productos?'
                        )
                        
                        Message.objects.create(
                            conversation=conv3,
                            sender_type='agent',
                            sender_user=agent,
                            sender_name=agent.get_full_name() or agent.username,
                            content='Claro, le envío toda la información por email. ¡Gracias por su interés!'
                        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up omnichannel data!')
        )