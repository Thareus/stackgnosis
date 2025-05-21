import React, { createContext, useContext, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { toast, ToastType } from "../components/Toast";

interface AuthContextType {
  accessToken: string | null;
  userEmail: string | null;
  isAuthenticated: boolean;
  setAccessToken: (token: string | null) => void;
  setUserEmail: (email: string | null) => void;
  handleLogout: () => void;
  ws: React.RefObject<ReconnectingWebSocket | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const [accessToken, setAccessToken] = useState<string | null>(localStorage.getItem('accessToken') || null);
  const [userEmail, setUserEmail] = useState<string | null>(localStorage.getItem('userEmail') || null);
  const ws = useRef<ReconnectingWebSocket | null>(null);
  const isAuthenticated = Boolean(accessToken && userEmail && accessToken.trim() !== '' && userEmail.trim() !== '');

  const handleLogout = useCallback(() => {
    console.log('Logging out');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userSlug');
    localStorage.removeItem('userName');
    setAccessToken(null);
    setUserEmail(null);
    // Close WebSocket connection if it exists
    if (ws.current) {
      console.log('Closing WebSocket connection.');
      ws.current.onclose = () => {
        ws.current = null;
      };
      ws.current.close();
    }
    navigate('/', { replace: true });
  }, [navigate]);

  // WebSocket connection and event handler logic
  React.useEffect(() => {
    if (accessToken && userEmail) {
      if (!ws.current || ws.current.readyState === WebSocket.CLOSED) {
        const wsUrl = `ws://127.0.0.1:8000/ws/notifications/?token=${accessToken}`;
        console.log(`Connecting to WebSocket: ${wsUrl}`);

        ws.current = new ReconnectingWebSocket(wsUrl, [], {
          maxRetries: 10,
          maxReconnectionDelay: 2000,
        });

        if (ws.current) {
          ws.current.onopen = () => {
            console.log("WebSocket connection opened");
          };

          ws.current.onmessage = (event: MessageEvent) => {
            try {
              const data = JSON.parse(event.data);
              console.log("WebSocket message received:", data);

              if (data.type === 'connection_established') {
                console.log(data.message);
              } else if (data.type === 'send_notification') {
                if (toast) {
                  const toastType = data.message_type as ToastType;
                  toast[toastType](data.message, data.linkUrl, data.linkLabel);
                } else {
                  console.log('Notification:', data.message);
                }
              } else {
                console.warn("Received unknown message type:", data.type);
              }
            } catch (error) {
              console.error("Failed to parse WebSocket message or handle it:", error);
            }
          };

          ws.current.onerror = (error: any) => {
            console.error("WebSocket error:", error);
            if (error.message && error.message.includes("401")) {
              console.error("Unauthorized WebSocket connection. Logging out.");
              handleLogout();
            }
          };

          ws.current.onclose = (event: any) => {
            console.log("WebSocket connection closed:", event.code, event.reason);
            const unauthorized = event.code === 4001 || event.code === 1008 ||
              (typeof event.reason === 'string' && event.reason.toLowerCase().includes('403')) ||
              (typeof event.reason === 'string' && event.reason.toLowerCase().includes('unauthorized'));
            if (unauthorized) {
              console.error("WebSocket closed due to unauthorized/forbidden (code:", event.code, ", reason:", event.reason, "). Redirecting to login.");
              handleLogout();
            }
          };
        }
      }
    } else {
      if (ws.current) {
        console.log("Closing WebSocket connection due to logout.");
        ws.current.close();
        ws.current = null;
      }
    }
    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        console.log("Closing WebSocket connection on cleanup.");
        ws.current.close();
      }
    };
  }, [accessToken, userEmail, ws, handleLogout]);


  return (
    <AuthContext.Provider value={{ accessToken, userEmail, isAuthenticated, setAccessToken, setUserEmail, handleLogout, ws }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
