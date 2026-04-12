// API service for Spatial Canvas
import { API_BASE_URL } from '../config';
import { getToken, authService } from './auth';

const makeAuthRequest = async (path, options = {}) => {
  const token = await getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  // Attempt token refresh on 401
  if (response.status === 401) {
    const refreshResult = await authService.refreshToken();
    if (refreshResult.success) {
      const newToken = await getToken();
      headers['Authorization'] = `Bearer ${newToken}`;
      return fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    }
    throw new Error('Authentication required');
  }
  return response;
};

export const anchorAPI = {
  createAnchor: async (data) => {
    const response = await makeAuthRequest('/api/v1/anchors', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create anchor');
    }
    return response.json();
  },

  getNearbyAnchors: async (lat, lng, radius = 1.0) => {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/anchors?latitude=${lat}&longitude=${lng}&radius_km=${radius}`
    );
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch anchors');
    }
    return response.json();
  },

  getMyAnchors: async () => {
    const response = await makeAuthRequest('/api/v1/anchors/mine');
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch user anchors');
    }
    return response.json();
  },

  deleteAnchor: async (anchorId) => {
    const response = await makeAuthRequest(`/api/v1/anchors/${anchorId}`, {
      method: 'DELETE',
    });
    if (response.status !== 204 && !response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to delete anchor');
    }
    return true;
  },
};
