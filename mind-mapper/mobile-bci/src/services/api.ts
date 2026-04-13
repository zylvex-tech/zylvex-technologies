import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { getToken, storeToken, clearToken } from './auth';
import { API_BASE_URL, AUTH_BASE_URL } from '../config';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
});

// Request interceptor to add token
api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const refreshToken = await SecureStore.getItemAsync('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const response = await fetch(`${AUTH_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (response.ok) {
          const data = await response.json();
          await storeToken(data.access_token);
          if (data.refresh_token) {
            await SecureStore.setItemAsync('refresh_token', data.refresh_token);
          }
          // Retry the original request with the new token
          error.config.headers['Authorization'] = `Bearer ${data.access_token}`;
          return api.request(error.config);
        }
      } catch {
        await clearToken();
        // Navigation to Login should be handled by the component catching the error
      }
    }
    return Promise.reject(error);
  }
);

export const getMindMaps = async () => {
  const response = await api.get('/mindmaps');
  return response.data;
};

export const createMindMap = async (title: string) => {
  const response = await api.post('/mindmaps', { title });
  return response.data;
};

export const deleteMindMap = async (id: string) => {
  const response = await api.delete(`/mindmaps/${id}`);
  return response.data;
};

export const getMindMapNodes = async (mindmapId: string) => {
  const response = await api.get(`/mindmaps/${mindmapId}/nodes`);
  return response.data;
};

export const getMindMapSessions = async (mindmapId: string) => {
  const response = await api.get(`/mindmaps/${mindmapId}/sessions`);
  return response.data;
};

export const createNode = async (mindmapId: string, nodeData: any) => {
  const response = await api.post(`/mindmaps/${mindmapId}/nodes`, nodeData);
  return response.data;
};

export const updateNode = async (mindmapId: string, nodeId: string, nodeData: any) => {
  const response = await api.put(`/mindmaps/${mindmapId}/nodes/${nodeId}`, nodeData);
  return response.data;
};

export const deleteNode = async (mindmapId: string, nodeId: string) => {
  const response = await api.delete(`/mindmaps/${mindmapId}/nodes/${nodeId}`);
  return response.data;
};

export const saveSession = async (mindmapId: string, sessionData: any) => {
  const response = await api.post(`/mindmaps/${mindmapId}/sessions`, sessionData);
  return response.data;
};

export default api;
