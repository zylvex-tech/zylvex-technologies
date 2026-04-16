export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AnchorResponse {
  id: string;
  user_id: string;
  title: string;
  content: string;
  content_type: string;
  latitude: number;
  longitude: number;
  created_at: string;
  updated_at: string;
}

export interface AnchorCreate {
  title: string;
  content: string;
  content_type: string;
  latitude: number;
  longitude: number;
}

export interface AnchorsListResponse {
  anchors: AnchorResponse[];
  count: number;
  radius_km: number;
}

export interface MindMapResponse {
  id: string;
  user_id: string;
  title: string;
  node_count: number;
  created_at: string;
  updated_at: string;
}

export interface NodeResponse {
  id: string;
  mindmap_id: string;
  text: string;
  focus_level: number;
  color: string;
  x: number;
  y: number;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface NodeCreate {
  text: string;
  focus_level: number;
  color: string;
  x: number;
  y: number;
  parent_id?: string | null;
}

export interface NodeUpdate {
  text?: string;
  focus_level?: number;
  color?: string;
  x?: number;
  y?: number;
  parent_id?: string | null;
}

export interface SessionResponse {
  mindmap_id: string;
  avg_focus: number;
  duration_seconds: number;
  node_count: number;
  focus_timeline: number[];
  created_at: string;
}

export interface SessionCreate {
  avg_focus: number;
  duration_seconds: number;
  node_count: number;
  focus_timeline: number[];
}
