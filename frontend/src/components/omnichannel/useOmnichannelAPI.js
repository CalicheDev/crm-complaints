import { useState, useCallback } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const useOmnichannelAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const makeRequest = useCallback(async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('authToken');
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Authorization': `Token ${token}`,
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const get = useCallback((endpoint) => {
    return makeRequest(endpoint, { method: 'GET' });
  }, [makeRequest]);

  const post = useCallback((endpoint, data) => {
    return makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }, [makeRequest]);

  const patch = useCallback((endpoint, data) => {
    return makeRequest(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }, [makeRequest]);

  const put = useCallback((endpoint, data) => {
    return makeRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }, [makeRequest]);

  const del = useCallback((endpoint) => {
    return makeRequest(endpoint, { method: 'DELETE' });
  }, [makeRequest]);

  return {
    loading,
    error,
    get,
    post,
    patch,
    put,
    delete: del,
    makeRequest,
  };
};

export default useOmnichannelAPI;