// Auth service for SPATIAL CANVAS mobile app

import * as SecureStore from 'expo-secure-store';
import { AUTH_BASE_URL } from '../config';

// Token storage keys
const ACCESS_TOKEN_KEY = 'spatial_canvas_access_token';
const REFRESH_TOKEN_KEY = 'spatial_canvas_refresh_token';
const USER_DATA_KEY = 'spatial_canvas_user_data';

// Standalone token accessor used by other services
export const getToken = async () => SecureStore.getItemAsync(ACCESS_TOKEN_KEY);

// Auth service API calls
export const authService = {
  // Register new user
  async register(fullName, email, password) {
    try {
      const response = await fetch(`${AUTH_BASE_URL}/auth/register`, {
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
      const response = await fetch(`${AUTH_BASE_URL}/auth/login`, {
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

      // Fetch user profile from /auth/me
      const meResponse = await fetch(`${AUTH_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      });
      if (meResponse.ok) {
        const userData = await meResponse.json();
        await SecureStore.setItemAsync(
          USER_DATA_KEY,
          JSON.stringify({ id: userData.id, email: userData.email, full_name: userData.full_name })
        );
      }

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
        await fetch(`${AUTH_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
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

  // Refresh access token (token rotation: new refresh token is also returned)
  async refreshToken() {
    try {
      const refreshToken = await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);

      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${AUTH_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const tokenData = await response.json();
      await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokenData.access_token);
      await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokenData.refresh_token);

      return { success: true, accessToken: tokenData.access_token };
    } catch (error) {
      console.error('Token refresh error:', error);
      return { success: false, error: error.message };
    }
  },
};
