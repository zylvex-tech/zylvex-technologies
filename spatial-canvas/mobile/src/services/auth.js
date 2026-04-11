// Auth service for SPATIAL CANVAS mobile app

import * as SecureStore from 'expo-secure-store';

const AUTH_SERVICE_URL = 'http://localhost:8001';
const BACKEND_URL = 'http://localhost:8000';

// Token storage keys
const ACCESS_TOKEN_KEY = 'spatial_canvas_access_token';
const REFRESH_TOKEN_KEY = 'spatial_canvas_refresh_token';
const USER_DATA_KEY = 'spatial_canvas_user_data';

// Auth service API calls
export const authService = {
  // Register new user
  async register(fullName, email, password) {
    try {
      const response = await fetch(`${AUTH_SERVICE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          full_name: fullName,
          email: email,
          password: password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const userData = await response.json();
      return { success: true, user: userData };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: error.message };
    }
  },

  // Login user
  async login(email, password) {
    try {
      const response = await fetch(`${AUTH_SERVICE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const tokenData = await response.json();
      
      // Store tokens securely
      await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokenData.access_token);
      await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokenData.refresh_token);
      
      // Store user data
      await SecureStore.setItemAsync(USER_DATA_KEY, JSON.stringify({
        id: tokenData.user_id,
        email: email,
        full_name: tokenData.full_name,
      }));

      return { success: true, tokens: tokenData };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  },

  // Logout user
  async logout() {
    try {
      const refreshToken = await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
      
      if (refreshToken) {
        // Call logout endpoint to revoke refresh token
        await fetch(`${AUTH_SERVICE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${refreshToken}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local storage
      await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
      await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
      await SecureStore.deleteItemAsync(USER_DATA_KEY);
    }
  },

  // Get current access token
  async getAccessToken() {
    return await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
  },

  // Check if user is authenticated
  async isAuthenticated() {
    const token = await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
    return !!token;
  },

  // Get user data
  async getUserData() {
    const userData = await SecureStore.getItemAsync(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
  },

  // Refresh access token
  async refreshToken() {
    try {
      const refreshToken = await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
      
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${AUTH_SERVICE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const tokenData = await response.json();
      await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokenData.access_token);
      
      return { success: true, accessToken: tokenData.access_token };
    } catch (error) {
      console.error('Token refresh error:', error);
      return { success: false, error: error.message };
    }
  },
};

// API service with auth headers
export const apiService = {
  // Make authenticated API call
  async makeRequest(url, options = {}) {
    const accessToken = await SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const response = await fetch(`${BACKEND_URL}${url}`, {
      ...options,
      headers,
    });

    // Handle token expiration
    if (response.status === 401) {
      // Try to refresh token
      const refreshResult = await authService.refreshToken();
      
      if (refreshResult.success) {
        // Retry request with new token
        return this.makeRequest(url, options);
      } else {
        // Refresh failed, user needs to login again
        throw new Error('Authentication required');
      }
    }

    return response;
  },

  // Create anchor
  async createAnchor(anchorData) {
    const response = await this.makeRequest('/api/v1/anchors', {
      method: 'POST',
      body: JSON.stringify(anchorData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create anchor');
    }

    return await response.json();
  },

  // Get nearby anchors
  async getNearbyAnchors(latitude, longitude, radiusKm = 1.0) {
    const response = await fetch(
      `${BACKEND_URL}/api/v1/anchors?latitude=${latitude}&longitude=${longitude}&radius_km=${radiusKm}`
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch anchors');
    }

    return await response.json();
  },

  // Get user's anchors
  async getMyAnchors() {
    const response = await this.makeRequest('/api/v1/anchors/mine');

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch user anchors');
    }

    return await response.json();
  },

  // Delete anchor
  async deleteAnchor(anchorId) {
    const response = await this.makeRequest(`/api/v1/anchors/${anchorId}`, {
      method: 'DELETE',
    });

    if (!response.status !== 204) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to delete anchor');
    }

    return true;
  },
};
