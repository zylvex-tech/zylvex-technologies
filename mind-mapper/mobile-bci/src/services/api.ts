import axios from 'axios';
import { getToken } from './auth';

const API_BASE_URL = 'http://localhost:8002/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
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

export const createNode = async (mindmapId: string, nodeData: any) => {
  const response = await api.post(`/mindmaps/${mindmapId}/nodes`, nodeData);
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
