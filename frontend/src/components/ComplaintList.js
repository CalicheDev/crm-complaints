import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ApiService from '../services/api';
import LoadingSpinner from './common/LoadingSpinner';
import Alert from './common/Alert';

const ComplaintList = ({ userComplaints = false, agentComplaints = false }) => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);
  const { user, hasRole } = useAuth();

  useEffect(() => {
    fetchComplaints();
  }, [userComplaints, agentComplaints]);

  const fetchComplaints = async () => {
    try {
      setLoading(true);
      let data;
      
      if (userComplaints) {
        data = await ApiService.getMyComplaints();
      } else if (agentComplaints) {
        data = await ApiService.getAgentComplaints();
      } else {
        data = await ApiService.getComplaints();
      }
      
      setComplaints(data.results || data);
    } catch (error) {
      setAlert({ type: 'error', message: error.message });
    } finally {
      setLoading(false);
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

  const getTitle = () => {
    if (userComplaints) return 'My Complaints';
    if (agentComplaints) return 'Assigned Complaints';
    return 'All Complaints';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{getTitle()}</h1>
        {!agentComplaints && (
          <Link
            to="/complaint-form"
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
          >
            New Complaint
          </Link>
        )}
      </div>

      {alert && (
        <Alert
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      {complaints.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">
            {userComplaints
              ? "You haven't submitted any complaints yet."
              : agentComplaints
              ? "No complaints assigned to you yet."
              : "No complaints found."}
          </div>
          {!agentComplaints && (
            <Link
              to="/complaint-form"
              className="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium transition-colors duration-200"
            >
              Submit Your First Complaint
            </Link>
          )}
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {complaints.map((complaint) => (
              <li key={complaint.id}>
                <Link
                  to={`/complaints/${complaint.id}`}
                  className="block hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-blue-600 truncate">
                          {complaint.title}
                        </p>
                        <div className="mt-2 flex items-center text-sm text-gray-500">
                          <span className="truncate">
                            {complaint.created_by 
                              ? `Created by: ${complaint.created_by.username}`
                              : `PQRS: ${complaint.citizen_name || 'Anonymous'} (${complaint.complaint_type || 'Queja'})`
                            }
                          </span>
                          {complaint.assigned_to && (
                            <>
                              <span className="mx-2">•</span>
                              <span>
                                Assigned to: {complaint.assigned_to.username}
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="ml-2 flex-shrink-0 flex items-center space-x-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                            complaint.status
                          )}`}
                        >
                          {getStatusText(complaint.status)}
                        </span>
                        <div className="text-sm text-gray-500">
                          {new Date(complaint.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Stats section for admins */}
      {hasRole('admin') && !userComplaints && !agentComplaints && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center">
                    <span className="text-yellow-600 text-sm font-medium">P</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Pending
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {complaints.filter(c => c.status === 'pending').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                    <span className="text-blue-600 text-sm font-medium">IP</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      In Progress
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {complaints.filter(c => c.status === 'in_progress').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
                    <span className="text-green-600 text-sm font-medium">R</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Resolved
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {complaints.filter(c => c.status === 'resolved').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComplaintList;