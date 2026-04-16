/**
 * NotificationsContext
 *
 * Opens a WebSocket connection to the realtime gateway when the user is
 * logged in. Listens for incoming push events and:
 *   1. Shows a toast notification for each event.
 *   2. Updates the unread count badge in the nav.
 *   3. Prepends the event to the local notifications list.
 *
 * Reconnect strategy: exponential back-off capped at 30 s.
 * The context also exposes the paginated notification list and helpers
 * to mark notifications read.
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import type { NotificationItem, WsEvent } from '../api/types';
import {
  fetchNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '../api/notifications';
import { useAuth } from './auth';
import { useToast } from '../components/Toast';

const REALTIME_URL =
  (import.meta.env.VITE_REALTIME_WS_URL as string | undefined) ??
  'ws://localhost:8004';

const MAX_RECONNECT_DELAY_MS = 30_000;

// ─── Event → human-readable label ───────────────────────────────────────────

function eventLabel(event: WsEvent): string | null {
  const title = (event.data?.title as string | undefined) ?? '';
  if (title) return title;

  switch (event.event) {
    case 'new_follow':
      return 'You have a new follower!';
    case 'new_reaction':
      return 'Someone reacted to your content.';
    case 'new_nearby_anchor':
      return 'A new anchor was placed nearby.';
    case 'new_collaboration_invite':
      return 'You received a collaboration invite.';
    default:
      return null;
  }
}

// ─── Context shape ───────────────────────────────────────────────────────────

interface NotificationsContextValue {
  notifications: NotificationItem[];
  unreadCount: number;
  isLoading: boolean;
  loadNotifications: () => Promise<void>;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
}

const NotificationsContext = createContext<NotificationsContextValue | null>(null);

// ─── Provider ────────────────────────────────────────────────────────────────

export function NotificationsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { state: authState } = useAuth();
  const { showToast } = useToast();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  // ── Load notifications from API ──────────────────────────────────────────

  const loadNotifications = useCallback(async () => {
    if (!authState.user) return;
    setIsLoading(true);
    try {
      const data = await fetchNotifications(1, 20);
      setNotifications(data.items);
    } catch {
      // Silently ignore — user might not be connected yet
    } finally {
      setIsLoading(false);
    }
  }, [authState.user]);

  // ── Mark a single notification read ─────────────────────────────────────

  const markRead = useCallback(
    async (id: string) => {
      try {
        await markNotificationRead(id);
        setNotifications((prev) =>
          prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
        );
      } catch {
        // ignore
      }
    },
    [],
  );

  // ── Mark all notifications read ──────────────────────────────────────────

  const markAllRead = useCallback(async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch {
      // ignore
    }
  }, []);

  // ── WebSocket lifecycle ──────────────────────────────────────────────────

  const connectWs = useCallback(() => {
    if (!authState.user || !authState.accessToken) return;

    const userId = authState.user.id;
    const token = authState.accessToken;
    const url = `${REALTIME_URL}/ws/${userId}?token=${encodeURIComponent(token)}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      reconnectAttemptRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const msg: WsEvent = JSON.parse(event.data as string);
        if (msg.event === 'ping' || msg.event === 'connected') return;

        // Show toast
        const label = eventLabel(msg);
        if (label) showToast(label, 'info');

        // Prepend to local list as a synthetic notification item
        if (msg.data) {
          const syntheticNotif: NotificationItem = {
            id: (msg.data.id as string | undefined) ?? crypto.randomUUID(),
            user_id: userId,
            type: msg.data.type as NotificationItem['type'],
            title: (msg.data.title as string | undefined) ?? label ?? '',
            body: (msg.data.body as string | undefined) ?? '',
            metadata: (msg.data.metadata as Record<string, unknown> | undefined) ?? {},
            read: false,
            created_at: new Date().toISOString(),
          };
          setNotifications((prev) => [syntheticNotif, ...prev].slice(0, 50));
        }
      } catch {
        // ignore malformed messages
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    ws.onclose = () => {
      wsRef.current = null;
      // Exponential back-off reconnect
      const attempt = reconnectAttemptRef.current;
      const delay = Math.min(500 * Math.pow(2, attempt), MAX_RECONNECT_DELAY_MS);
      reconnectAttemptRef.current = attempt + 1;
      reconnectTimerRef.current = setTimeout(() => {
        connectWs();
      }, delay);
    };
  }, [authState.user, authState.accessToken, showToast]);

  // ── Connect/disconnect on auth state change ──────────────────────────────

  useEffect(() => {
    if (!authState.user || !authState.accessToken) {
      // Logged out — close any open connection
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      if (wsRef.current) {
        // Prevent auto-reconnect on deliberate logout
        wsRef.current.onclose = null;
        wsRef.current.close();
        wsRef.current = null;
      }
      setNotifications([]);
      reconnectAttemptRef.current = 0;
      return;
    }

    // Logged in — load initial notifications and open WS
    loadNotifications();
    connectWs();

    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, [authState.user?.id, authState.accessToken, loadNotifications, connectWs]);

  return (
    <NotificationsContext.Provider
      value={{
        notifications,
        unreadCount,
        isLoading,
        loadNotifications,
        markRead,
        markAllRead,
      }}
    >
      {children}
    </NotificationsContext.Provider>
  );
}

// ─── Hook ────────────────────────────────────────────────────────────────────

export function useNotifications(): NotificationsContextValue {
  const ctx = useContext(NotificationsContext);
  if (!ctx)
    throw new Error('useNotifications must be used within NotificationsProvider');
  return ctx;
}
