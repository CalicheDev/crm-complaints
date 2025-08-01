import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import LoadingSpinner from './common/LoadingSpinner';
import Alert from './common/Alert';
import Modal from './common/Modal';

const AtencionManager = ({ complaintId, refreshComplaint }) => {
  const { user, hasRole } = useAuth();
  const [atenciones, setAtenciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [currentAtencion, setCurrentAtencion] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    observacion: '',
    tipo_contacto: 'telefono',
    resultado: 'contactado'
  });

  useEffect(() => {
    fetchAtenciones();
  }, [complaintId]);

  const fetchAtenciones = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getAtenciones(complaintId);
      
      // Handle different response formats
      if (Array.isArray(data)) {
        setAtenciones(data);
      } else if (data && Array.isArray(data.results)) {
        // Paginated response
        setAtenciones(data.results);
      } else if (data && Array.isArray(data.data)) {
        // Wrapped response
        setAtenciones(data.data);
      } else {
        console.error('Unexpected response format:', data);
        setAtenciones([]);
        setAlert({ type: 'error', message: 'Formato de respuesta inesperado del servidor' });
      }
    } catch (error) {
      console.error('Error fetching atenciones:', error);
      setAtenciones([]);
      setAlert({ type: 'error', message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      
      if (currentAtencion) {
        // Update existing atencion
        await ApiService.updateAtencion(currentAtencion.id, formData);
        setAlert({ type: 'success', message: 'Atención actualizada exitosamente' });
        setShowEditModal(false);
      } else {
        // Create new atencion
        await ApiService.createAtencion(complaintId, formData);
        setAlert({ type: 'success', message: 'Atención agregada exitosamente' });
        setShowAddModal(false);
      }
      
      resetForm();
      fetchAtenciones();
      if (refreshComplaint) refreshComplaint();
    } catch (error) {
      setAlert({ type: 'error', message: error.message });
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (atencion) => {
    setCurrentAtencion(atencion);
    setFormData({
      observacion: atencion.observacion,
      tipo_contacto: atencion.tipo_contacto,
      resultado: atencion.resultado
    });
    setShowEditModal(true);
  };

  const handleDelete = async (atencionId) => {
    if (!window.confirm('¿Está seguro de que desea eliminar esta atención?')) {
      return;
    }

    try {
      await ApiService.deleteAtencion(atencionId);
      setAlert({ type: 'success', message: 'Atención eliminada exitosamente' });
      fetchAtenciones();
      if (refreshComplaint) refreshComplaint();
    } catch (error) {
      setAlert({ type: 'error', message: error.message });
    }
  };

  const resetForm = () => {
    setFormData({
      observacion: '',
      tipo_contacto: 'telefono',
      resultado: 'contactado'
    });
    setCurrentAtencion(null);
  };

  const handleModalClose = () => {
    setShowAddModal(false);
    setShowEditModal(false);
    resetForm();
  };

  const getContactTypeText = (tipo) => {
    const types = {
      telefono: 'Teléfono',
      email: 'Email',
      presencial: 'Presencial',
      chat: 'Chat',
      otro: 'Otro'
    };
    return types[tipo] || tipo;
  };

  const getResultText = (resultado) => {
    const results = {
      contactado: 'Contactado exitosamente',
      no_contactado: 'No se pudo contactar',
      informacion_adicional: 'Se obtuvo información adicional',
      seguimiento_requerido: 'Requiere seguimiento',
      resuelto: 'Resuelto en esta atención'
    };
    return results[resultado] || resultado;
  };

  const getResultColor = (resultado) => {
    switch (resultado) {
      case 'contactado':
        return 'bg-green-100 text-green-800';
      case 'no_contactado':
        return 'bg-red-100 text-red-800';
      case 'informacion_adicional':
        return 'bg-blue-100 text-blue-800';
      case 'seguimiento_requerido':
        return 'bg-yellow-100 text-yellow-800';
      case 'resuelto':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const canManageAtenciones = () => {
    return hasRole('agent') || hasRole('admin');
  };

  if (!canManageAtenciones()) {
    return null;
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Atenciones</h3>
            <p className="mt-1 text-sm text-gray-500">
              Registro de contactos y seguimientos realizados
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Agregar Atención
          </button>
        </div>
      </div>

      {alert && (
        <div className="px-4 py-3">
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        </div>
      )}

      <div className="px-4 py-5 sm:p-6">
        {loading ? (
          <div className="flex justify-center">
            <LoadingSpinner size="medium" />
          </div>
        ) : !Array.isArray(atenciones) || atenciones.length === 0 ? (
          <div className="text-center text-gray-500 py-6">
            <p>No hay atenciones registradas para esta queja.</p>
            <p className="text-sm mt-1">Agrega la primera atención para comenzar el seguimiento.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {Array.isArray(atenciones) && atenciones.map((atencion) => (
              <div key={atencion.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-900">
                      {atencion.agent?.first_name} {atencion.agent?.last_name} 
                      <span className="text-gray-500">(@{atencion.agent?.username})</span>
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(atencion.created_at).toLocaleString()}
                    </span>
                  </div>
                  
                  {(atencion.agent?.id === user?.id || hasRole('admin')) && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(atencion)}
                        className="text-blue-600 hover:text-blue-500 text-sm"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(atencion.id)}
                        className="text-red-600 hover:text-red-500 text-sm"
                      >
                        Eliminar
                      </button>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                  <div>
                    <span className="text-xs font-medium text-gray-500">Tipo de Contacto:</span>
                    <p className="text-sm text-gray-900">{getContactTypeText(atencion.tipo_contacto)}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-gray-500">Resultado:</span>
                    <div className="mt-1">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getResultColor(atencion.resultado)}`}>
                        {getResultText(atencion.resultado)}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-gray-500">Fecha:</span>
                    <p className="text-sm text-gray-900">
                      {new Date(atencion.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div>
                  <span className="text-xs font-medium text-gray-500">Observación:</span>
                  <p className="text-sm text-gray-900 mt-1 whitespace-pre-wrap">{atencion.observacion}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      <Modal
        isOpen={showAddModal || showEditModal}
        onClose={handleModalClose}
        title={currentAtencion ? 'Editar Atención' : 'Agregar Atención'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="observacion" className="block text-sm font-medium text-gray-700 mb-2">
              Observación *
            </label>
            <textarea
              id="observacion"
              value={formData.observacion}
              onChange={(e) => setFormData({ ...formData, observacion: e.target.value })}
              rows={4}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Describe los detalles del contacto y las acciones realizadas..."
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="tipo_contacto" className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Contacto
              </label>
              <select
                id="tipo_contacto"
                value={formData.tipo_contacto}
                onChange={(e) => setFormData({ ...formData, tipo_contacto: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="telefono">Teléfono</option>
                <option value="email">Email</option>
                <option value="presencial">Presencial</option>
                <option value="chat">Chat</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            <div>
              <label htmlFor="resultado" className="block text-sm font-medium text-gray-700 mb-2">
                Resultado
              </label>
              <select
                id="resultado"
                value={formData.resultado}
                onChange={(e) => setFormData({ ...formData, resultado: e.target.value })}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="contactado">Contactado exitosamente</option>
                <option value="no_contactado">No se pudo contactar</option>
                <option value="informacion_adicional">Se obtuvo información adicional</option>
                <option value="seguimiento_requerido">Requiere seguimiento</option>
                <option value="resuelto">Resuelto en esta atención</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={handleModalClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting || !formData.observacion.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? <LoadingSpinner size="small" /> : (currentAtencion ? 'Actualizar' : 'Agregar')}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AtencionManager;