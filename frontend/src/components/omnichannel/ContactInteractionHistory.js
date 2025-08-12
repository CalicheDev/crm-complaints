import React, { useState, useEffect } from 'react';
// import { formatDistanceToNow } from 'date-fns';
// import { es } from 'date-fns/locale';
import LoadingSpinner from '../common/LoadingSpinner';

const ContactInteractionHistory = ({ contactId, currentConversation }) => {
  const [contact, setContact] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('history');

  useEffect(() => {
    if (contactId) {
      loadContactInfo();
      loadInteractionHistory();
    }
  }, [contactId]);

  const loadContactInfo = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/omnichannel/contacts/${contactId}/interaction_summary/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setContact(data);
      }
    } catch (err) {
      console.error('Error loading contact info:', err);
    }
  };

  const loadInteractionHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/omnichannel/interactions/?contact=${contactId}`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setHistory(data.results || data);
      }
    } catch (err) {
      console.error('Error loading interaction history:', err);
    } finally {
      setLoading(false);
    }
  };

  const getInteractionIcon = (interactionType) => {
    switch (interactionType) {
      case 'complaint_created':
        return '📝';
      case 'conversation_started':
        return '💬';
      case 'message_sent':
        return '📤';
      case 'call_made':
        return '📞';
      case 'email_sent':
        return '📧';
      case 'status_changed':
        return '🔄';
      case 'agent_assigned':
        return '👤';
      case 'resolution_provided':
        return '✅';
      case 'follow_up':
        return '📋';
      default:
        return '📊';
    }
  };

  const getInteractionColor = (interactionType) => {
    switch (interactionType) {
      case 'complaint_created':
        return 'text-red-600 bg-red-100';
      case 'conversation_started':
        return 'text-blue-600 bg-blue-100';
      case 'message_sent':
        return 'text-green-600 bg-green-100';
      case 'call_made':
        return 'text-purple-600 bg-purple-100';
      case 'email_sent':
        return 'text-yellow-600 bg-yellow-100';
      case 'status_changed':
        return 'text-orange-600 bg-orange-100';
      case 'agent_assigned':
        return 'text-indigo-600 bg-indigo-100';
      case 'resolution_provided':
        return 'text-green-700 bg-green-200';
      case 'follow_up':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="flex items-center justify-center h-32">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Información del Cliente</h3>
        
        {/* Tabs */}
        <div className="mt-3 flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('info')}
            className={`flex-1 px-3 py-1 text-sm rounded-md transition-colors ${
              activeTab === 'info'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Información
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 px-3 py-1 text-sm rounded-md transition-colors ${
              activeTab === 'history'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Historial
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'info' && contact && (
          <div className="p-4 space-y-4">
            {/* Información básica */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Datos de Contacto</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-600">Nombre:</span>
                  <span className="ml-2">{contact.name}</span>
                </div>
                {contact.email && (
                  <div>
                    <span className="font-medium text-gray-600">Email:</span>
                    <span className="ml-2">{contact.email}</span>
                  </div>
                )}
                {contact.phone && (
                  <div>
                    <span className="font-medium text-gray-600">Teléfono:</span>
                    <span className="ml-2">{contact.phone}</span>
                  </div>
                )}
                {contact.whatsapp_number && (
                  <div>
                    <span className="font-medium text-gray-600">WhatsApp:</span>
                    <span className="ml-2">{contact.whatsapp_number}</span>
                  </div>
                )}
                {contact.document && (
                  <div>
                    <span className="font-medium text-gray-600">Documento:</span>
                    <span className="ml-2">{contact.document}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Estadísticas */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Estadísticas</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {contact.total_conversations}
                  </div>
                  <div className="text-xs text-blue-600">Conversaciones</div>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {contact.total_complaints}
                  </div>
                  <div className="text-xs text-green-600">PQRS</div>
                </div>
              </div>
            </div>

            {/* Canales preferidos */}
            {contact.preferred_channels && contact.preferred_channels.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Canales Preferidos</h4>
                <div className="space-y-2">
                  {contact.preferred_channels.map((channel, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span>{channel.channel}</span>
                      <span className="text-gray-500">{channel.usage_count} veces</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Información relacionada con la queja actual */}
            {currentConversation?.complaint && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">PQRS Relacionada</h4>
                <div className="bg-gray-50 p-3 rounded-lg text-sm">
                  <div className="font-medium">{currentConversation.complaint.title}</div>
                  <div className="text-gray-600 mt-1">
                    Tipo: {currentConversation.complaint.complaint_type}
                  </div>
                  <div className="text-gray-600">
                    Estado: {currentConversation.complaint.status}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="p-4">
            {history.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <p>No hay historial de interacciones</p>
              </div>
            ) : (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 mb-3">
                  Historial de Interacciones ({history.length})
                </h4>
                
                <div className="space-y-3">
                  {history.map((interaction) => (
                    <div key={interaction.id} className="flex space-x-3">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${getInteractionColor(interaction.interaction_type)}`}>
                        {getInteractionIcon(interaction.interaction_type)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900">
                          {interaction.interaction_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </div>
                        
                        <div className="text-sm text-gray-600 mt-1">
                          {interaction.description}
                        </div>
                        
                        <div className="flex items-center mt-2 text-xs text-gray-500 space-x-2">
                          <span>
                            {new Date(interaction.created_at).toLocaleString()}
                          </span>
                          
                          {interaction.agent && (
                            <>
                              <span>•</span>
                              <span>{interaction.agent.first_name} {interaction.agent.last_name}</span>
                            </>
                          )}
                          
                          {interaction.channel && (
                            <>
                              <span>•</span>
                              <span>{interaction.channel.name}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContactInteractionHistory;