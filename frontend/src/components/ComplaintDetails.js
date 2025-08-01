import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import LoadingSpinner from './common/LoadingSpinner';
import Alert from './common/Alert';
import Modal from './common/Modal';
import AtencionManager from './AtencionManager';

const ComplaintDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, hasRole } = useAuth();
  
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchComplaint();
    if (hasRole('admin')) {
      fetchAgents();
    }
  }, [id]);

  const fetchComplaint = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getComplaint(id);
      setComplaint(data);
    } catch (error) {
      setAlert({ type: 'error', message: error.message });
      if (error.status === 404) {
        setTimeout(() => navigate('/complaints'), 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchAgents = async () => {
    try {
      const data = await ApiService.getAvailableAgents();
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      setUpdating(true);
      const updatedComplaint = await ApiService.updateComplaintStatus(id, newStatus);
      setComplaint(updatedComplaint.complaint);
      setAlert({ type: 'success', message: 'Status updated successfully' });
    } catch (error) {
      setAlert({ type: 'error', message: error.message });
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignAgent = async () => {
    if (!selectedAgent) {
      setAlert({ type: 'error', message: 'Please select an agent' });
      return;
    }

    try {
      setUpdating(true);
      const updatedComplaint = await ApiService.assignComplaint(id, selectedAgent);
      setComplaint(updatedComplaint.complaint);
      setShowAssignModal(false);
      setSelectedAgent('');
      setAlert({ type: 'success', message: 'Agent assigned successfully' });
    } catch (error) {
      setAlert({ type: 'error', message: error.message });
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this complaint?')) {
      return;
    }

    try {
      setUpdating(true);
      await ApiService.deleteComplaint(id);
      setAlert({ type: 'success', message: 'Complaint deleted successfully' });
      setTimeout(() => navigate('/complaints'), 1000);
    } catch (error) {
      setAlert({ type: 'error', message: error.message });
      setUpdating(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'in_progress':
        return 'In Progress';
      case 'resolved':
        return 'Resolved';
      default:
        return status;
    }
  };

  const canUpdateStatus = () => {
    return hasRole('admin') || hasRole('agent') || complaint?.created_by?.id === user?.id;
  };

  const canAssignAgent = () => {
    return hasRole('admin');
  };

  const canDelete = () => {
    return hasRole('admin');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!complaint) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Complaint not found</div>
        <Link
          to="/complaints"
          className="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium"
        >
          Back to Complaints
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Link
            to="/complaints"
            className="text-blue-600 hover:text-blue-500 text-sm font-medium"
          >
            ← Back to Complaints
          </Link>
        </div>
        <div className="flex items-center space-x-2">
          {canAssignAgent() && (
            <button
              onClick={() => setShowAssignModal(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm font-medium"
              disabled={updating}
            >
              Assign Agent
            </button>
          )}
          {canDelete() && (
            <button
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-medium"
              disabled={updating}
            >
              Delete
            </button>
          )}
        </div>
      </div>

      {alert && (
        <Alert
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">{complaint.title}</h1>
          <div className="mt-2 flex items-center space-x-4">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                complaint.status
              )}`}
            >
              {getStatusText(complaint.status)}
            </span>
            <span className="text-sm text-gray-500">
              Created: {new Date(complaint.created_at).toLocaleString()}
            </span>
            {complaint.updated_at !== complaint.created_at && (
              <span className="text-sm text-gray-500">
                Updated: {new Date(complaint.updated_at).toLocaleString()}
              </span>
            )}
          </div>
        </div>

        <div className="px-4 py-5 sm:p-6">
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{complaint.description}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Created By</h4>
                <p className="text-sm text-gray-600">
                  {complaint.created_by?.username || 'Anonymous'}
                  {complaint.created_by?.first_name && (
                    <span className="ml-2">
                      ({complaint.created_by.first_name} {complaint.created_by.last_name})
                    </span>
                  )}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Assigned To</h4>
                <p className="text-sm text-gray-600">
                  {complaint.assigned_to?.username || 'Not assigned'}
                  {complaint.assigned_to?.first_name && (
                    <span className="ml-2">
                      ({complaint.assigned_to.first_name} {complaint.assigned_to.last_name})
                    </span>
                  )}
                </p>
              </div>
            </div>

            {canUpdateStatus() && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3">Update Status</h4>
                <div className="flex space-x-2">
                  {['pending', 'in_progress', 'resolved'].map((status) => (
                    <button
                      key={status}
                      onClick={() => handleStatusUpdate(status)}
                      disabled={complaint.status === status || updating}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors duration-200 ${
                        complaint.status === status
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {getStatusText(status)}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Atenciones Section */}
      <AtencionManager complaintId={id} refreshComplaint={fetchComplaint} />

      {/* Assign Agent Modal */}
      <Modal
        isOpen={showAssignModal}
        onClose={() => setShowAssignModal(false)}
        title="Assign Agent"
      >
        <div className="space-y-4">
          <div>
            <label htmlFor="agent" className="block text-sm font-medium text-gray-700 mb-2">
              Select Agent
            </label>
            <select
              id="agent"
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Choose an agent...</option>
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.username} - {agent.first_name} {agent.last_name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowAssignModal(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
            >
              Cancel
            </button>
            <button
              onClick={handleAssignAgent}
              disabled={updating || !selectedAgent}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {updating ? <LoadingSpinner size="small" /> : 'Assign'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ComplaintDetails;