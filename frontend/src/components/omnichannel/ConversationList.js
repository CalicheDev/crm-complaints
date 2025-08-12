import React from 'react';
// import { formatDistanceToNow } from 'date-fns';
// import { es } from 'date-fns/locale';

const ConversationList = ({ conversations, selectedConversation, onConversationSelect }) => {
  const getChannelIcon = (channelType) => {
    switch (channelType) {
      case 'email':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
            <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
          </svg>
        );
      case 'whatsapp':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.700" />
          </svg>
        );
      case 'facebook':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
          </svg>
        );
      case 'phone':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
          </svg>
        );
      case 'chat':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'waiting':
        return 'bg-yellow-100 text-yellow-800';
      case 'resolved':
        return 'bg-blue-100 text-blue-800';
      case 'closed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatLastMessage = (lastMessage) => {
    if (!lastMessage) return 'Sin mensajes';
    
    if (lastMessage.message_type === 'text') {
      return lastMessage.content?.substring(0, 60) + (lastMessage.content?.length > 60 ? '...' : '');
    } else {
      return `[${lastMessage.message_type.toUpperCase()}]`;
    }
  };

  if (!conversations || conversations.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>No hay conversaciones disponibles</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {conversations.map((conversation) => (
        <div
          key={conversation.id}
          onClick={() => onConversationSelect(conversation)}
          className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
            selectedConversation?.id === conversation.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
          }`}
        >
          {/* Header de la conversación */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              {/* Ícono del canal */}
              <div className={`flex-shrink-0 p-1 rounded text-gray-600`}>
                {getChannelIcon(conversation.channel.channel_type)}
              </div>
              
              {/* Nombre del contacto */}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">
                  {conversation.contact.name}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {conversation.channel.name}
                </p>
              </div>
            </div>

            {/* Badges de estado y prioridad */}
            <div className="flex flex-col items-end space-y-1">
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(conversation.status)}`}>
                {conversation.status}
              </span>
              {conversation.priority !== 'medium' && (
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(conversation.priority)}`}>
                  {conversation.priority}
                </span>
              )}
            </div>
          </div>

          {/* Asunto de la conversación */}
          {conversation.subject && (
            <div className="mt-2">
              <p className="text-sm text-gray-700 truncate">
                <strong>Asunto:</strong> {conversation.subject}
              </p>
            </div>
          )}

          {/* Último mensaje */}
          <div className="mt-2">
            <p className="text-sm text-gray-600 truncate">
              {conversation.last_message ? (
                <>
                  <span className="font-medium">
                    {conversation.last_message.sender_name}:
                  </span>{' '}
                  {formatLastMessage(conversation.last_message)}
                </>
              ) : (
                'Sin mensajes'
              )}
            </p>
          </div>

          {/* Información de tiempo y mensajes no leídos */}
          <div className="mt-2 flex items-center justify-between">
            <p className="text-xs text-gray-500">
              {new Date(conversation.last_activity).toLocaleString()}
            </p>
            
            {conversation.unread_count > 0 && (
              <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                {conversation.unread_count}
              </span>
            )}
          </div>

          {/* Agente asignado */}
          {conversation.agent && (
            <div className="mt-2">
              <p className="text-xs text-gray-500">
                <strong>Agente:</strong> {conversation.agent.first_name} {conversation.agent.last_name || conversation.agent.username}
              </p>
            </div>
          )}

          {/* Tags */}
          {conversation.tags && conversation.tags.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {conversation.tags.slice(0, 2).map((tagAssignment) => (
                <span
                  key={tagAssignment.id}
                  className="inline-flex px-2 py-1 text-xs font-medium rounded"
                  style={{
                    backgroundColor: tagAssignment.tag.color + '20',
                    color: tagAssignment.tag.color,
                  }}
                >
                  {tagAssignment.tag.name}
                </span>
              ))}
              {conversation.tags.length > 2 && (
                <span className="inline-flex px-2 py-1 text-xs text-gray-500">
                  +{conversation.tags.length - 2}
                </span>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ConversationList;