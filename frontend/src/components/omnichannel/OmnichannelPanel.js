import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import ConversationList from './ConversationList';
import ConversationView from './ConversationView';
import ChannelSelector from './ChannelSelector';
import ContactInteractionHistory from './ContactInteractionHistory';
import LoadingSpinner from '../common/LoadingSpinner';
import useOmnichannelAPI from './useOmnichannelAPI';

const OmnichannelPanel = () => {
  const { user } = useAuth();
  const api = useOmnichannelAPI();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('active');
  const [selectedChannel, setSelectedChannel] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadConversations();
  }, [activeFilter, selectedChannel, searchTerm]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadChannels(),
        loadConversations()
      ]);
    } catch (err) {
      setError('Error cargando datos iniciales');
      console.error('Error loading initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadChannels = async () => {
    try {
      const data = await api.get('/api/omnichannel/channels/');
      setChannels(data);
    } catch (err) {
      console.error('Error loading channels:', err);
    }
  };

  const loadConversations = async () => {
    try {
      const params = new URLSearchParams();
      if (activeFilter !== 'all') params.append('status', activeFilter);
      if (selectedChannel !== 'all') params.append('channel', selectedChannel);
      if (searchTerm) params.append('search', searchTerm);

      const data = await api.get(`/api/omnichannel/conversations/?${params}`);
      setConversations(data.results || data);
    } catch (err) {
      setError('Error cargando conversaciones');
      console.error('Error loading conversations:', err);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
  };

  const handleConversationUpdate = (updatedConversation) => {
    setConversations(prev => 
      prev.map(conv => 
        conv.id === updatedConversation.id ? updatedConversation : conv
      )
    );
    setSelectedConversation(updatedConversation);
  };

  const handleNewMessage = (conversationId, message) => {
    // Actualizar la conversación con el nuevo mensaje
    setConversations(prev =>
      prev.map(conv => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            last_message: {
              content: message.content,
              message_type: message.message_type,
              sender_type: message.sender_type,
              sender_name: message.sender_name,
              created_at: message.created_at,
            },
            last_activity: message.created_at,
          };
        }
        return conv;
      })
    );

    // Si la conversación está seleccionada, recargarla
    if (selectedConversation && selectedConversation.id === conversationId) {
      loadConversationDetail(conversationId);
    }
  };

  const loadConversationDetail = async (conversationId) => {
    try {
      const conversation = await api.get(`/api/omnichannel/conversations/${conversationId}/`);
      setSelectedConversation(conversation);
    } catch (err) {
      console.error('Error loading conversation detail:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Panel lateral - Lista de conversaciones */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        {/* Header del panel */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">Omnicanal</h2>
          
          {/* Filtros */}
          <div className="mt-4 space-y-3">
            {/* Filtro por estado */}
            <div>
              <select
                value={activeFilter}
                onChange={(e) => setActiveFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todas las conversaciones</option>
                <option value="active">Activas</option>
                <option value="waiting">Esperando</option>
                <option value="resolved">Resueltas</option>
                <option value="closed">Cerradas</option>
              </select>
            </div>

            {/* Filtro por canal */}
            <ChannelSelector
              channels={channels}
              selectedChannel={selectedChannel}
              onChannelChange={setSelectedChannel}
            />

            {/* Búsqueda */}
            <div>
              <input
                type="text"
                placeholder="Buscar conversaciones..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Lista de conversaciones */}
        <div className="flex-1 overflow-y-auto">
          <ConversationList
            conversations={conversations}
            selectedConversation={selectedConversation}
            onConversationSelect={handleConversationSelect}
          />
        </div>
      </div>

      {/* Panel principal - Vista de conversación */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <ConversationView
            conversation={selectedConversation}
            onConversationUpdate={handleConversationUpdate}
            onNewMessage={handleNewMessage}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <div className="mb-4">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.478 8-10 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.478-8 10-8s10 3.582 10 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900">Selecciona una conversación</h3>
              <p className="text-gray-500">Elige una conversación de la lista para ver los mensajes e historial.</p>
            </div>
          </div>
        )}
      </div>

      {/* Panel derecho - Historial de interacciones (opcional) */}
      {selectedConversation && (
        <div className="w-80 bg-white border-l border-gray-200">
          <ContactInteractionHistory
            contactId={selectedConversation.contact.id}
            currentConversation={selectedConversation}
          />
        </div>
      )}
    </div>
  );
};

export default OmnichannelPanel;