import axios from 'axios';

// Base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service class
class ApiService {
  // Authentication endpoints
  static async register(userData) {
    try {
      const response = await apiClient.post('/api/auth/register/', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async login(credentials) {
    try {
      const response = await apiClient.post('/api/auth/login/', credentials);
      const { data } = response.data;
      
      // Store token and user data
      localStorage.setItem('authToken', data.token);
      localStorage.setItem('userData', JSON.stringify(data.user));
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async logout() {
    try {
      await apiClient.post('/api/auth/logout/');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
    } catch (error) {
      // Even if logout fails on server, clear local storage
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      throw this.handleError(error);
    }
  }

  static async getUserProfile() {
    try {
      const response = await apiClient.get('/api/auth/profile/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async updateUserProfile(profileData) {
    try {
      const response = await apiClient.patch('/api/auth/profile/', profileData);
      // Update stored user data
      localStorage.setItem('userData', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async changePassword(passwordData) {
    try {
      const response = await apiClient.post('/api/auth/profile/change-password/', passwordData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Complaint endpoints
  static async getComplaints(params = {}) {
    try {
      const response = await apiClient.get('/api/complaints/', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async getComplaint(id) {
    try {
      const response = await apiClient.get(`/api/complaints/${id}/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async createComplaint(complaintData) {
    try {
      const response = await apiClient.post('/api/complaints/', complaintData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async updateComplaint(id, complaintData) {
    try {
      const response = await apiClient.patch(`/api/complaints/${id}/`, complaintData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async deleteComplaint(id) {
    try {
      const response = await apiClient.delete(`/api/complaints/${id}/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async assignComplaint(id, agentId) {
    try {
      const response = await apiClient.post(`/api/complaints/${id}/assign/`, {
        agent_id: agentId
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async updateComplaintStatus(id, status) {
    try {
      const response = await apiClient.patch(`/api/complaints/${id}/status/`, {
        status
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async getMyComplaints() {
    try {
      const response = await apiClient.get('/api/complaints/my/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async getAgentComplaints() {
    try {
      const response = await apiClient.get('/api/complaints/agent/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Dashboard endpoints
  static async getDashboardAnalytics() {
    try {
      const response = await apiClient.get('/api/complaints/dashboard/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // User management endpoints (admin only)
  static async getUsers() {
    try {
      const response = await apiClient.get('/api/auth/users/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async updateUserRole(userId, role) {
    try {
      const response = await apiClient.post(`/api/auth/users/${userId}/role/`, {
        role
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async activateUser(userId) {
    try {
      const response = await apiClient.post(`/api/auth/users/${userId}/activation/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async deactivateUser(userId) {
    try {
      const response = await apiClient.delete(`/api/auth/users/${userId}/activation/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async getUserStatistics() {
    try {
      const response = await apiClient.get('/api/auth/users/statistics/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async getAvailableAgents() {
    try {
      const response = await apiClient.get('/api/complaints/agents/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Utility methods
  static handleError(error) {
    const errorMessage = error.response?.data?.error || 
                        error.response?.data?.message || 
                        error.message || 
                        'An unexpected error occurred';
    
    const errorDetails = error.response?.data || {};
    
    return {
      message: errorMessage,
      status: error.response?.status,
      details: errorDetails
    };
  }

  static isAuthenticated() {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    return !!(token && userData);
  }

  static getCurrentUser() {
    const userData = localStorage.getItem('userData');
    return userData ? JSON.parse(userData) : null;
  }

  static getUserRole() {
    const user = this.getCurrentUser();
    if (!user || !user.groups || user.groups.length === 0) {
      return 'user';
    }
    return user.groups[0]; // Return first group as primary role
  }

  static hasRole(role) {
    const userRole = this.getUserRole();
    return userRole === role;
  }

  static isAdmin() {
    return this.hasRole('admin');
  }

  static isAgent() {
    return this.hasRole('agent');
  }
}

export default ApiService;