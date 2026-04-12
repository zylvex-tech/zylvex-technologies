import axios from 'axios';
import { getToken } from './auth';
import { API_BASE_URL } from '../config';

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
      // Token expired, redirect to login
      // This will be handled in the component
    }
    return Promise.reject(error);
  }
);

export const getMindMaps = async () => {
  const response = await api.get('/mindmaps');
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
