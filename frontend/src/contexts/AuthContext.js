import React, { createContext, useContext, useReducer, useEffect } from 'react';
import ApiService from '../services/api';

// Initial state
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
  error: null,
};

// Action types
const AuthActionTypes = {
  LOGIN_REQUEST: 'LOGIN_REQUEST',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  UPDATE_USER: 'UPDATE_USER',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AuthActionTypes.LOGIN_REQUEST:
      return {
        ...state,
        loading: true,
        error: null,
      };
    
    case AuthActionTypes.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
        error: null,
      };
    
    case AuthActionTypes.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: action.payload,
      };
    
    case AuthActionTypes.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      };
    
    case AuthActionTypes.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };
    
    case AuthActionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    
    case AuthActionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// AuthProvider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize authentication state on app load
  useEffect(() => {
    const initializeAuth = () => {
      const token = localStorage.getItem('authToken');
      const userData = localStorage.getItem('userData');

      if (token && userData) {
        try {
          const user = JSON.parse(userData);
          dispatch({
            type: AuthActionTypes.LOGIN_SUCCESS,
            payload: { user, token },
          });
        } catch (error) {
          console.error('Error parsing user data:', error);
          localStorage.removeItem('authToken');
          localStorage.removeItem('userData');
          dispatch({ type: AuthActionTypes.SET_LOADING, payload: false });
        }
      } else {
        dispatch({ type: AuthActionTypes.SET_LOADING, payload: false });
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (credentials) => {
    dispatch({ type: AuthActionTypes.LOGIN_REQUEST });

    try {
      const response = await ApiService.login(credentials);
      const { data } = response;

      dispatch({
        type: AuthActionTypes.LOGIN_SUCCESS,
        payload: {
          user: data.user,
          token: data.token,
        },
      });

      return response;
    } catch (error) {
      dispatch({
        type: AuthActionTypes.LOGIN_FAILURE,
        payload: error.message,
      });
      throw error;
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: AuthActionTypes.LOGIN_REQUEST });

    try {
      const response = await ApiService.register(userData);
      const { data } = response;

      dispatch({
        type: AuthActionTypes.LOGIN_SUCCESS,
        payload: {
          user: data.user,
          token: data.token,
        },
      });

      return response;
    } catch (error) {
      dispatch({
        type: AuthActionTypes.LOGIN_FAILURE,
        payload: error.message,
      });
      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await ApiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: AuthActionTypes.LOGOUT });
    }
  };

  // Update user profile
  const updateProfile = async (profileData) => {
    try {
      const updatedUser = await ApiService.updateUserProfile(profileData);
      dispatch({
        type: AuthActionTypes.UPDATE_USER,
        payload: updatedUser,
      });
      return updatedUser;
    } catch (error) {
      throw error;
    }
  };

  // Clear error
  const clearError = () => {
    dispatch({ type: AuthActionTypes.CLEAR_ERROR });
  };

  // Helper functions
  const hasRole = (role) => {
    if (!state.user || !state.user.groups) return false;
    return state.user.groups.includes(role);
  };

  const isAdmin = () => hasRole('admin');
  const isAgent = () => hasRole('agent');

  // Context value
  const value = {
    // State
    user: state.user,
    token: state.token,
    isAuthenticated: state.isAuthenticated,
    loading: state.loading,
    error: state.error,

    // Actions
    login,
    register,
    logout,
    updateProfile,
    clearError,

    // Helper functions
    hasRole,
    isAdmin,
    isAgent,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;