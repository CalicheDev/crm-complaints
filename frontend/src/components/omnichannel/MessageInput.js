import React, { useState, useRef } from 'react';

const MessageInput = ({ onSendMessage, disabled, sending }) => {
  const [message, setMessage] = useState('');
  const [attachment, setAttachment] = useState(null);
  const [attachmentPreview, setAttachmentPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!message.trim() && !attachment) return;
    if (disabled || sending) return;

    const messageData = {
      content: message.trim(),
      message_type: 'text',
    };

    // Si hay un archivo adjunto
    if (attachment) {
      // Determinar tipo de mensaje basado en el archivo
      if (attachment.type.startsWith('image/')) {
        messageData.message_type = 'image';
      } else {
        messageData.message_type = 'file';
      }
      
      messageData.attachment = attachment;
      messageData.attachment_name = attachment.name;
    }
    
    // Enviar mensaje (con o sin archivo)
    await onSendMessage(messageData);

    // Limpiar el formulario
    setMessage('');
    setAttachment(null);
    setAttachmentPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validar tamaño del archivo (máximo 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('El archivo es demasiado grande. El tamaño máximo es 10MB.');
      return;
    }

    setAttachment(file);

    // Crear vista previa para imágenes
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setAttachmentPreview({
          type: 'image',
          url: e.target.result,
          name: file.name
        });
      };
      reader.readAsDataURL(file);
    } else {
      setAttachmentPreview({
        type: 'file',
        name: file.name,
        size: file.size
      });
    }
  };

  const removeAttachment = () => {
    setAttachment(null);
    setAttachmentPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-4">
      {/* Vista previa del archivo adjunto */}
      {attachmentPreview && (
        <div className="mb-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {attachmentPreview.type === 'image' ? (
                <img
                  src={attachmentPreview.url}
                  alt="Vista previa"
                  className="w-12 h-12 object-cover rounded"
                />
              ) : (
                <div className="w-12 h-12 bg-gray-300 rounded flex items-center justify-center">
                  <svg className="w-6 h-6 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-900">{attachmentPreview.name}</p>
                {attachmentPreview.size && (
                  <p className="text-xs text-gray-500">{formatFileSize(attachmentPreview.size)}</p>
                )}
              </div>
            </div>
            <button
              onClick={removeAttachment}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Formulario de mensaje */}
      <form onSubmit={handleSubmit} className="flex items-end space-x-2">
        <div className="flex-1">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={disabled ? "Conversación cerrada" : "Escribe tu mensaje..."}
            disabled={disabled}
            rows={1}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            style={{ minHeight: '40px', maxHeight: '120px' }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
        </div>

        {/* Botón de archivo */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="image/*,.pdf,.doc,.docx,.txt"
          className="hidden"
          disabled={disabled}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="p-2 text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </button>

        {/* Botón de enviar */}
        <button
          type="submit"
          disabled={disabled || sending || (!message.trim() && !attachment)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {sending ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Enviando...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              <span>Enviar</span>
            </>
          )}
        </button>
      </form>

      {/* Ayuda rápida */}
      <div className="mt-2 text-xs text-gray-500">
        <p>Presiona Shift+Enter para nueva línea • Archivos máximo 10MB</p>
      </div>
    </div>
  );
};

export default MessageInput;