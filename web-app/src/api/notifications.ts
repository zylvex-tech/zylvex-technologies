import { getAccessToken } from './client';
import type { NotificationItem, PaginatedNotifications } from './types';

const NOTIFICATIONS_URL = import.meta.env.VITE_NOTIFICATIONS_API_URL ?? 'http://localhost:8005';

async function notificationsRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> ?? {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${NOTIFICATIONS_URL}${path}`, { ...options, headers });
  if (res.status === 204) return undefined as T;
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      message = err.detail ?? err.message ?? message;
    } catch { /* ignore */ }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export async function fetchNotifications(
  page = 1,
  pageSize = 20,
): Promise<PaginatedNotifications> {
  return notificationsRequest<PaginatedNotifications>(
    `/notifications/me?page=${page}&page_size=${pageSize}`,
  );
}

export async function markNotificationRead(id: string): Promise<NotificationItem> {
  return notificationsRequest<NotificationItem>(
    `/notifications/mark-read/${id}`,
    { method: 'POST' },
  );
}

export async function markAllNotificationsRead(): Promise<{ marked_read: number }> {
  return notificationsRequest<{ marked_read: number }>(
    '/notifications/mark-all-read',
    { method: 'POST' },
  );
}
