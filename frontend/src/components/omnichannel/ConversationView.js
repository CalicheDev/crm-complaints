import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
// import { formatDistanceToNow } from 'date-fns';
// import { es } from 'date-fns/locale';
import MessageInput from './MessageInput';
import LoadingSpinner from '../common/LoadingSpinner';

const ConversationView = ({ conversation, onConversationUpdate, onNewMessage }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (conversation) {
      loadMessages();
    }
  }, [conversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/omnichannel/conversations/${conversation.id}/messages/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data.results || data);
      }
    } catch (err) {
      console.error('Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (messageData) => {
    try {
      setSending(true);
      const response = await fetch(`http://localhost:8000/api/omnichannel/conversations/${conversation.id}/send_message/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(messageData),
      });

      if (response.ok) {
        const newMessage = await response.json();
        setMessages(prev => [...prev, newMessage]);
        onNewMessage(conversation.id, newMessage);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error enviando mensaje');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      alert('Error enviando mensaje: ' + err.message);
    } finally {
      setSending(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/api/omnichannel/conversations/${conversation.id}/update_status/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        const updatedConversation = await response.json();
        onConversationUpdate(updatedConversation);
      }
    } catch (err) {
      console.error('Error updating status:', err);
    }
  };

  const getMessageAlignment = (message) => {
    return message.sender_type === 'agent' ? 'justify-end' : 'justify-start';
  };

  const getMessageBubbleStyle = (message) => {
    if (message.sender_type === 'agent') {
      return 'bg-blue-500 text-white ml-auto';
    } else if (message.sender_type === 'system') {
      return 'bg-gray-200 text-gray-700 mx-auto text-center';
    } else {
      return 'bg-gray-100 text-gray-900';
    }
  };

  const formatMessageTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const renderMessageContent = (message) => {
    switch (message.message_type) {
      case 'text':
        return <p className="whitespace-pre-wrap">{message.content}</p>;
      
      case 'image':
        return (
          <div>
            {message.content && <p className="mb-2">{message.content}</p>}
            <img
              src={message.attachment}
              alt="Imagen adjunta"
              className="max-w-xs rounded-lg cursor-pointer"
              onClick={() => window.open(message.attachment, '_blank')}
            />
          </div>
        );
      
      case 'file':
        return (
          <div>
            {message.content && <p className="mb-2">{message.content}</p>}
            <a
              href={message.attachment}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 p-2 bg-gray-50 rounded border hover:bg-gray-100"
            >
              <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium">{message.attachment_name}</span>
              {message.attachment_size_mb && (
                <span className="text-xs text-gray-500">({message.attachment_size_mb} MB)</span>
              )}
            </a>
          </div>
        );
      
      case 'system':
        return (
          <p className="text-sm font-medium italic">
            {message.content}
          </p>
        );
      
      default:
        return <p>{message.content}</p>;
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header de la conversación */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {conversation.contact.name}
            </h3>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>{conversation.channel.name}</span>
              {conversation.contact.email && (
                <span>{conversation.contact.email}</span>
              )}
              {conversation.contact.phone && (
                <span>{conversation.contact.phone}</span>
              )}
            </div>
            {conversation.subject && (
              <p className="text-sm text-gray-600 mt-1">
                <strong>Asunto:</strong> {conversation.subject}
              </p>
            )}
          </div>

          {/* Controles de estado */}
          <div className="flex items-center space-x-2">
            <select
              value={conversation.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="active">Activa</option>
              <option value="waiting">Esperando</option>
              <option value="resolved">Resuelta</option>
              <option value="closed">Cerrada</option>
            </select>
          </div>
        </div>
      </div>

      {/* Área de mensajes */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>No hay mensajes en esta conversación</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`flex ${getMessageAlignment(message)}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${getMessageBubbleStyle(message)}`}>
                {/* Nombre del remitente (solo para mensajes del contacto) */}
                {message.sender_type !== 'agent' && message.sender_type !== 'system' && (
                  <p className="text-xs font-medium mb-1">
                    {message.sender_name}
                  </p>
                )}

                {/* Contenido del mensaje */}
                <div className="break-words">
                  {renderMessageContent(message)}
                </div>

                {/* Timestamp */}
                <p className={`text-xs mt-1 ${
                  message.sender_type === 'agent' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {formatMessageTime(message.created_at)}
                  {message.sender_type === 'agent' && (
                    <span className="ml-1">
                      {message.is_delivered ? '✓✓' : '✓'}
                    </span>
                  )}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input de mensaje */}
      <div className="border-t border-gray-200 bg-white">
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={sending || conversation.status === 'closed'}
          sending={sending}
        />
      </div>
    </div>
  );
};

export default ConversationView;