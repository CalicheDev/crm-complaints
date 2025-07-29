import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import ApiService from "../../services/api";
import LoadingSpinner from "../common/LoadingSpinner";
import Alert from "../common/Alert";

const UserRoleManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState({});
  const [alert, setAlert] = useState(null);
  const [actionLoading, setActionLoading] = useState({});
  
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setAlert(null);
      const response = await ApiService.getUsers();
      setUsers(response.results || response);
    } catch (error) {
      console.error("Error fetching users:", error);
      setAlert({
        type: "error",
        message: error.message || "Failed to load users"
      });
      if (error.status === 401) {
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const updateRole = async (userId) => {
    const newRole = selectedRole[userId];
    if (!newRole) {
      setAlert({
        type: "warning",
        message: "Please select a role first"
      });
      return;
    }

    try {
      setActionLoading({ ...actionLoading, [userId]: true });
      setAlert(null);
      
      const response = await ApiService.updateUserRole(userId, newRole);
      
      setAlert({
        type: "success",
        message: response.message || "Role updated successfully"
      });
      
      // Clear the selected role for this user
      setSelectedRole({ ...selectedRole, [userId]: "" });
      
      // Refresh the user list
      await fetchUsers();
    } catch (error) {
      console.error("Error updating role:", error);
      setAlert({
        type: "error",
        message: error.message || "Failed to update role"
      });
      if (error.status === 401) {
        handleLogout();
      }
    } finally {
      setActionLoading({ ...actionLoading, [userId]: false });
    }
  };

  const toggleUserActivation = async (userId, isActive) => {
    try {
      setActionLoading({ ...actionLoading, [`activation_${userId}`]: true });
      setAlert(null);
      
      let response;
      if (isActive) {
        response = await ApiService.deactivateUser(userId);
      } else {
        response = await ApiService.activateUser(userId);
      }
      
      setAlert({
        type: "success",
        message: response.message || `User ${isActive ? 'deactivated' : 'activated'} successfully`
      });
      
      // Refresh the user list
      await fetchUsers();
    } catch (error) {
      console.error("Error toggling user activation:", error);
      setAlert({
        type: "error",
        message: error.message || "Failed to update user status"
      });
    } finally {
      setActionLoading({ ...actionLoading, [`activation_${userId}`]: false });
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'agent':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatRoleName = (role) => {
    switch (role) {
      case 'admin':
        return 'Administrator';
      case 'agent':
        return 'Agent';
      default:
        return 'User';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">User Role Management</h1>
        <button
          onClick={fetchUsers}
          disabled={loading}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      {alert && (
        <Alert
          type={alert.type}
          className="mb-4"
          onClose={() => setAlert(null)}
        >
          {alert.message}
        </Alert>
      )}

      {users.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No users found.</div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-700">
                              {user.username.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.full_name || user.username}
                          </div>
                          <div className="text-sm text-gray-500">
                            @{user.username}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{user.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(user.groups?.[0])}`}>
                        {formatRoleName(user.groups?.[0])}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-y-2">
                      <div className="flex items-center space-x-2">
                        <select
                          value={selectedRole[user.id] || ""}
                          onChange={(e) =>
                            setSelectedRole({ ...selectedRole, [user.id]: e.target.value })
                          }
                          className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select Role</option>
                          <option value="admin">Administrator</option>
                          <option value="agent">Agent</option>
                        </select>
                        <button
                          onClick={() => updateRole(user.id)}
                          disabled={actionLoading[user.id] || !selectedRole[user.id]}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {actionLoading[user.id] ? (
                            <LoadingSpinner size="xs" className="text-white" />
                          ) : (
                            'Update'
                          )}
                        </button>
                      </div>
                      <div>
                        <button
                          onClick={() => toggleUserActivation(user.id, user.is_active)}
                          disabled={actionLoading[`activation_${user.id}`]}
                          className={`${
                            user.is_active 
                              ? 'bg-red-600 hover:bg-red-700' 
                              : 'bg-green-600 hover:bg-green-700'
                          } text-white px-3 py-1 rounded text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
                        >
                          {actionLoading[`activation_${user.id}`] ? (
                            <LoadingSpinner size="xs" className="text-white" />
                          ) : (
                            user.is_active ? 'Deactivate' : 'Activate'
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserRoleManagement;
