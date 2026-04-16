import { apiClient } from './client';
import type {
  MindMapResponse,
  NodeResponse,
  NodeCreate,
  NodeUpdate,
  SessionResponse,
  SessionCreate,
} from './types';

export function listMindmaps(): Promise<MindMapResponse[]> {
  return apiClient.get<MindMapResponse[]>('mindmapper', '/api/v1/mindmaps');
}

export function createMindmap(title: string): Promise<MindMapResponse> {
  return apiClient.post<MindMapResponse>('mindmapper', '/api/v1/mindmaps', { title });
}

export function deleteMindmap(id: string): Promise<void> {
  return apiClient.delete<void>('mindmapper', `/api/v1/mindmaps/${id}`);
}

export function listNodes(mindmapId: string): Promise<NodeResponse[]> {
  return apiClient.get<NodeResponse[]>('mindmapper', `/api/v1/mindmaps/${mindmapId}/nodes`);
}

export function createNode(mindmapId: string, data: NodeCreate): Promise<NodeResponse> {
  return apiClient.post<NodeResponse>('mindmapper', `/api/v1/mindmaps/${mindmapId}/nodes`, data);
}

export function updateNode(
  mindmapId: string,
  nodeId: string,
  data: NodeUpdate,
): Promise<NodeResponse> {
  return apiClient.put<NodeResponse>(
    'mindmapper',
    `/api/v1/mindmaps/${mindmapId}/nodes/${nodeId}`,
    data,
  );
}

export function deleteNode(mindmapId: string, nodeId: string): Promise<void> {
  return apiClient.delete<void>('mindmapper', `/api/v1/mindmaps/${mindmapId}/nodes/${nodeId}`);
}

export function listSessions(mindmapId: string): Promise<SessionResponse[]> {
  return apiClient.get<SessionResponse[]>('mindmapper', `/api/v1/mindmaps/${mindmapId}/sessions`);
}

export function createSession(mindmapId: string, data: SessionCreate): Promise<SessionResponse> {
  return apiClient.post<SessionResponse>(
    'mindmapper',
    `/api/v1/mindmaps/${mindmapId}/sessions`,
    data,
  );
}
