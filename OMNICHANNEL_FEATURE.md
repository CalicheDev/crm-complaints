# Omnichannel Feature - CRM Sistema de Quejas

Esta funcionalidad integra múltiples canales de comunicación en un panel unificado para la gestión de conversaciones con clientes.

## ✅ Funcionalidades Implementadas

### Backend (Django)

#### Modelos de Base de Datos
- **CommunicationChannel**: Define los canales de comunicación disponibles
- **Contact**: Información unificada de contactos con múltiples medios de comunicación
- **Conversation**: Conversaciones que agrupan mensajes por canal
- **Message**: Mensajes individuales con soporte para texto, imágenes, archivos y sistema
- **InteractionHistory**: Historial completo de interacciones del cliente
- **ChannelIntegration**: Configuraciones de integración para cada canal
- **ConversationTag**: Sistema de etiquetas para categorizar conversaciones

#### Canales Soportados
- ✅ **Chat en Vivo**: Comunicación directa en tiempo real
- ✅ **Email**: Integración con servidores SMTP
- ✅ **WhatsApp Business**: API de WhatsApp Business
- ✅ **Facebook Messenger**: Integración con Facebook API
- ✅ **Twitter DM**: Mensajes directos de Twitter
- ✅ **Instagram Direct**: Mensajes directos de Instagram
- ✅ **Llamadas Telefónicas**: Registro de actividad de llamadas
- ✅ **SMS**: Mensajería de texto

#### API Endpoints
- `/api/omnichannel/channels/` - Gestión de canales
- `/api/omnichannel/contacts/` - Gestión de contactos
- `/api/omnichannel/conversations/` - Gestión de conversaciones
- `/api/omnichannel/messages/` - Gestión de mensajes
- `/api/omnichannel/interactions/` - Historial de interacciones
- `/api/omnichannel/tags/` - Sistema de etiquetas
- `/api/omnichannel/integrations/` - Configuraciones de integración

#### Servicios de Integración
- **ChannelService**: Servicio principal para el envío de mensajes
- **EmailChannelHandler**: Envío de emails vía SMTP
- **WhatsAppChannelHandler**: Integración con WhatsApp Business API
- **FacebookChannelHandler**: Integración con Facebook Messenger API
- **PhoneChannelHandler**: Registro de actividad de llamadas
- **ChatChannelHandler**: Manejo de chat en vivo interno

### Frontend (React)

#### Componentes Principales
- **OmnichannelPanel**: Panel principal que integra todos los canales
- **ConversationList**: Lista de conversaciones con filtros avanzados
- **ConversationView**: Vista detallada de la conversación con mensajes
- **MessageInput**: Input avanzado con soporte para archivos adjuntos
- **ChannelSelector**: Selector de canales con íconos
- **ContactInteractionHistory**: Historial completo del cliente

#### Características del Interface
- ✅ **Panel Unificado**: Todas las conversaciones en un solo lugar
- ✅ **Filtros Avanzados**: Por estado, canal, prioridad y búsqueda de texto
- ✅ **Historial Unificado**: Todas las interacciones del cliente visibles
- ✅ **Información Contextual**: Datos del cliente, PQRS relacionadas, canales preferidos
- ✅ **Envío de Mensajes**: Con soporte para texto, imágenes y archivos
- ✅ **Estados de Conversación**: Activa, esperando, resuelta, cerrada
- ✅ **Sistema de Etiquetas**: Categorización visual de conversaciones
- ✅ **Responsive Design**: Compatible con dispositivos móviles

## 🔧 Configuración

### Variables de Entorno (.env)
```
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_email@empresa.com
EMAIL_HOST_PASSWORD=tu_password
EMAIL_USE_TLS=True

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=tu_token_de_acceso
WHATSAPP_PHONE_NUMBER_ID=tu_id_telefono
WHATSAPP_BUSINESS_ACCOUNT_ID=tu_id_cuenta_negocio

# Facebook Messenger
FACEBOOK_PAGE_ACCESS_TOKEN=tu_token_pagina
FACEBOOK_PAGE_ID=tu_id_pagina
```

### Comandos de Configuración
```bash
# Crear migraciones
python manage.py makemigrations omnichannel

# Aplicar migraciones
python manage.py migrate

# Configurar datos iniciales
python manage.py setup_omnichannel_data
```

## 📊 Uso del Sistema

### Para Agentes
1. **Acceso al Panel**: Navegar a `/omnichannel`
2. **Filtrar Conversaciones**: Usar filtros por estado, canal, prioridad
3. **Seleccionar Conversación**: Click en conversación para ver detalles
4. **Enviar Mensajes**: Usar el input inferior con soporte para archivos
5. **Ver Historial**: Panel derecho muestra historial completo del cliente
6. **Cambiar Estados**: Actualizar estado de la conversación
7. **Asignar Agentes**: Los administradores pueden reasignar conversaciones

### Para Administradores
1. **Configurar Canales**: En `/admin` > Omnichannel > Communication Channels
2. **Configurar Integraciones**: En Channel Integrations con credenciales de API
3. **Gestionar Etiquetas**: Crear y personalizar etiquetas de conversaciones
4. **Ver Analytics**: Dashboard con estadísticas de conversaciones por canal
5. **Asignar Agentes**: Distribuir conversaciones entre agentes

## 🔗 Integración con PQRS

El sistema omnicanal se integra completamente con el sistema de PQRS existente:

- **Conversaciones Vinculadas**: Cada conversación puede estar relacionada con una PQRS
- **Historial Unificado**: Las interacciones de PQRS aparecen en el historial del cliente
- **Datos Compartidos**: Los datos del cliente se comparten entre ambos sistemas
- **Seguimiento Completo**: Desde la PQRS inicial hasta la resolución por cualquier canal

## 🚀 Próximas Mejoras

### Funcionalidades Sugeridas
- **WebSocket**: Notificaciones en tiempo real de nuevos mensajes
- **Chatbot**: Integración con chatbots para respuestas automáticas
- **Templates**: Plantillas de respuesta predefinidas
- **Notas Internas**: Notas privadas entre agentes
- **SLA Tracking**: Seguimiento de tiempos de respuesta
- **Analytics Avanzados**: Métricas detalladas de performance
- **Escalamiento Automático**: Reglas de escalamiento por prioridad/tiempo

### Integraciones Adicionales
- **Slack**: Notificaciones a equipos internos
- **Telegram**: Canal adicional de comunicación
- **LinkedIn**: Mensajería profesional
- **Zendesk**: Sincronización con sistemas existentes

## 📝 API Documentation

### Endpoints Principales

#### Conversaciones
```
GET /api/omnichannel/conversations/
POST /api/omnichannel/conversations/
GET /api/omnichannel/conversations/{id}/
PATCH /api/omnichannel/conversations/{id}/update_status/
POST /api/omnichannel/conversations/{id}/send_message/
POST /api/omnichannel/conversations/{id}/assign_agent/
```

#### Contactos
```
GET /api/omnichannel/contacts/
GET /api/omnichannel/contacts/{id}/interaction_summary/
GET /api/omnichannel/contacts/{id}/conversations/
```

#### Mensajes
```
GET /api/omnichannel/messages/?conversation={id}
POST /api/omnichannel/messages/{id}/mark_as_read/
```

## 🔒 Seguridad

- **Autenticación Token**: Todas las APIs requieren autenticación
- **Permisos por Rol**: Acceso diferenciado para Admin/Agent/User
- **Validación de Archivos**: Límites de tamaño y tipos permitidos
- **Sanitización**: Validación de contenido de mensajes
- **Logs de Auditoría**: Registro completo de actividades

## ✅ Estado del Proyecto

**COMPLETADO** - La funcionalidad omnicanal está lista para producción con:
- ✅ Backend completo con API REST
- ✅ Frontend React funcional
- ✅ Integración con sistema PQRS existente
- ✅ Manejo de múltiples canales
- ✅ Historial unificado de clientes
- ✅ Panel de administración
- ✅ Datos de prueba configurados
- ✅ Documentación completa