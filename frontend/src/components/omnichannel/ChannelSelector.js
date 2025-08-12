import React from 'react';

const ChannelSelector = ({ channels, selectedChannel, onChannelChange }) => {
  const getChannelIcon = (channelType) => {
    switch (channelType) {
      case 'email':
        return '📧';
      case 'whatsapp':
        return '💬';
      case 'facebook':
        return '📘';
      case 'twitter':
        return '🐦';
      case 'instagram':
        return '📷';
      case 'phone':
        return '📞';
      case 'chat':
        return '💭';
      case 'sms':
        return '📱';
      default:
        return '💬';
    }
  };

  const getChannelName = (channelType) => {
    switch (channelType) {
      case 'email':
        return 'Email';
      case 'whatsapp':
        return 'WhatsApp';
      case 'facebook':
        return 'Facebook';
      case 'twitter':
        return 'Twitter';
      case 'instagram':
        return 'Instagram';
      case 'phone':
        return 'Teléfono';
      case 'chat':
        return 'Chat en Vivo';
      case 'sms':
        return 'SMS';
      default:
        return 'Desconocido';
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Canal
      </label>
      <select
        value={selectedChannel}
        onChange={(e) => onChannelChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="all">Todos los canales</option>
        {channels && Array.isArray(channels) && channels.map((channel) => (
          <option key={channel.id} value={channel.id}>
            {getChannelIcon(channel.channel_type)} {channel.name} ({getChannelName(channel.channel_type)})
          </option>
        ))}
      </select>
    </div>
  );
};

export default ChannelSelector;