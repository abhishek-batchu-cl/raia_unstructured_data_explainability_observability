/**
 * WebSocket Hook for Real-Time Updates
 * =====================================
 * Connects to RAIA backend WebSocket for real-time metric updates
 */

import { useEffect, useState, useRef, useCallback } from 'react';

export interface WebSocketMessage {
  type: string;
  data?: any;
  event?: any;
  channel?: string;
}

export interface UseWebSocketOptions {
  url?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export interface WebSocketState {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  error: Event | null;
  send: (message: any) => void;
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}): WebSocketState {
  const defaultWsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000`;
  const {
    url = `${defaultWsUrl}/ws`,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<Event | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError(err);
        onError?.(err);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        onDisconnect?.();

        // Auto-reconnect
        if (autoReconnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
    }
  }, [url, onConnect, onMessage, onDisconnect, onError, autoReconnect, reconnectInterval]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const subscribe = useCallback((channel: string) => {
    send({ type: 'subscribe', channel });
  }, [send]);

  const unsubscribe = useCallback((channel: string) => {
    send({ type: 'unsubscribe', channel });
  }, [send]);

  return {
    isConnected,
    lastMessage,
    error,
    send,
    subscribe,
    unsubscribe,
  };
}
