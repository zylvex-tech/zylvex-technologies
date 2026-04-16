const AUTH_URL = import.meta.env.VITE_AUTH_API_URL ?? 'http://localhost:8001';
const SPATIAL_URL = import.meta.env.VITE_SPATIAL_API_URL ?? 'http://localhost:8000';
const MIND_MAPPER_URL = import.meta.env.VITE_MIND_MAPPER_API_URL ?? 'http://localhost:8002';

let accessToken: string | null = null;
let refreshToken: string | null = null;
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

export function setTokens(access: string | null, refresh: string | null) {
  accessToken = access;
  refreshToken = refresh;
  if (refresh) {
    sessionStorage.setItem('refreshToken', refresh);
  } else {
    sessionStorage.removeItem('refreshToken');
  }
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getStoredRefreshToken(): string | null {
  return sessionStorage.getItem('refreshToken');
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
  sessionStorage.removeItem('refreshToken');
}

async function doRefresh(): Promise<string | null> {
  const rt = refreshToken ?? getStoredRefreshToken();
  if (!rt) return null;

  try {
    const res = await fetch(`${AUTH_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (!res.ok) {
      clearTokens();
      return null;
    }
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

async function refreshIfNeeded(): Promise<string | null> {
  if (!isRefreshing) {
    isRefreshing = true;
    refreshPromise = doRefresh().finally(() => {
      isRefreshing = false;
      refreshPromise = null;
    });
  }
  return refreshPromise!;
}

type ServiceKey = 'auth' | 'spatial' | 'mindmapper';

function getBaseUrl(service: ServiceKey): string {
  switch (service) {
    case 'auth': return AUTH_URL;
    case 'spatial': return SPATIAL_URL;
    case 'mindmapper': return MIND_MAPPER_URL;
  }
}

async function request<T>(
  service: ServiceKey,
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const base = getBaseUrl(service);
  const token = accessToken;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${base}${path}`, { ...options, headers });

  if (res.status === 401 && retry) {
    const newToken = await refreshIfNeeded();
    if (newToken) {
      return request<T>(service, path, options, false);
    }
    throw new ApiError(401, 'Unauthorized');
  }

  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const errData = await res.json();
      message = errData.detail ?? errData.message ?? message;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const apiClient = {
  get<T>(service: ServiceKey, path: string): Promise<T> {
    return request<T>(service, path, { method: 'GET' });
  },
  post<T>(service: ServiceKey, path: string, body?: unknown): Promise<T> {
    return request<T>(service, path, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  },
  put<T>(service: ServiceKey, path: string, body?: unknown): Promise<T> {
    return request<T>(service, path, {
      method: 'PUT',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  },
  delete<T>(service: ServiceKey, path: string): Promise<T> {
    return request<T>(service, path, { method: 'DELETE' });
  },
};
