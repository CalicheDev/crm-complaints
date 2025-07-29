import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import ApiService from "../services/api";
import LoadingSpinner from "./common/LoadingSpinner";
import Alert from "./common/Alert";

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await ApiService.getDashboardAnalytics();
        setData(response);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setError(error.message || "Failed to load dashboard data");
        if (error.status === 401) {
          handleLogout();
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <Alert type="error" className="m-4">
        {error}
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert type="warning" className="m-4">
        No dashboard data available
      </Alert>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <header className="mb-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Logout
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">T</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Complaints</dt>
                    <dd className="text-3xl font-semibold text-gray-900">{data.total_complaints}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">A</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Avg Resolution Time</dt>
                    <dd className="text-3xl font-semibold text-gray-900">
                      {data.avg_resolution_time ? 
                        `${Math.round(data.avg_resolution_time / 60)}m` : 
                        'N/A'
                      }
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
                  <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">P</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Pending</dt>
                    <dd className="text-3xl font-semibold text-gray-900">
                      {data.complaints_by_status?.find(s => s.status === 'pending')?.count || 0}
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
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">R</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Resolved</dt>
                    <dd className="text-3xl font-semibold text-gray-900">
                      {data.complaints_by_status?.find(s => s.status === 'resolved')?.count || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Complaints by Status
              </h3>
              <div className="space-y-3">
                {data.complaints_by_status?.map((status) => (
                  <div key={status.status} className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-500 capitalize">
                      {status.status.replace('_', ' ')}
                    </span>
                    <span className="text-2xl font-semibold text-gray-900">
                      {status.count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Agent Workload
              </h3>
              <div className="space-y-3">
                {data.agents_load?.length > 0 ? (
                  data.agents_load.map((agent) => (
                    <div key={agent.assigned_to__username} className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-500">
                        {agent.assigned_to__username}
                      </span>
                      <span className="text-2xl font-semibold text-gray-900">
                        {agent.count}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-sm">No agent assignments yet</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
