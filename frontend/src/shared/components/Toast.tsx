import React, { useEffect, useState } from "react";

// Toast types
export type ToastType = "success" | "error" | "info" | "warning";

export interface ToastMessage {
  id: number;
  message_type: ToastType;
  message: string;
  linkUrl?: string;
  linkLabel?: string;
}

let addToastHandler: ((msg: ToastMessage) => void) | null = null;

export const toast = {
  success: (message: string, linkUrl?: string, linkLabel?: string) => {
    addToastHandler && addToastHandler({ id: Date.now(), message, message_type: "success", linkUrl, linkLabel });
  },
  error: (message: string, linkUrl?: string, linkLabel?: string) => {
    addToastHandler && addToastHandler({ id: Date.now(), message, message_type: "error", linkUrl, linkLabel });
  },
  info: (message: string, linkUrl?: string, linkLabel?: string) => {
    addToastHandler && addToastHandler({ id: Date.now(), message, message_type: "info", linkUrl, linkLabel });
  },
  warning: (message: string, linkUrl?: string, linkLabel?: string) => {
    addToastHandler && addToastHandler({ id: Date.now(), message, message_type: "warning", linkUrl, linkLabel });
  },
};

interface ToastWithVisibility extends ToastMessage {
  visible: boolean;
}

const FADE_DURATION = 400; // ms
const DISPLAY_DURATION = 3000; // ms

interface ToastContentProps {
  message: string;
  message_type: ToastType;
  linkUrl?: string;
  linkLabel?: string;
}

const ToastContent: React.FC<ToastContentProps> = ({ message, message_type, linkUrl, linkLabel }) => {
  return (
    <>
      <p className={`toast-text toast-text-${message_type}`}>{message}</p>
      {linkUrl && linkLabel && (
        <a href={linkUrl} target="_blank" rel="noopener noreferrer">
          <button className={`toast-link-button toast-link-button-${message_type}`}>{linkLabel}</button>
        </a>
      )}
      {message_type === "error" && (
        <button className="toast-retry-button" onClick={() => window.location.reload()}>
          Retry
        </button>
      )}
    </>
  );
};

const Toast: React.FC = () => {
  const [toasts, setToasts] = useState<ToastWithVisibility[]>([]);

  useEffect(() => {
    addToastHandler = (msg: ToastMessage) => {
      setToasts((prev) => [...prev, { ...msg, visible: false }]);
      setTimeout(() => {
        setToasts((prev) =>
          prev.map((t) => (t.id === msg.id ? { ...t, visible: true } : t))
        );
      }, 20); // allow for mount before transition
      setTimeout(() => {
        setToasts((prev) =>
          prev.map((t) => (t.id === msg.id ? { ...t, visible: false } : t))
        );
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== msg.id));
        }, FADE_DURATION);
      }, DISPLAY_DURATION);
    };
    return () => {
      addToastHandler = null;
    };
  }, []);

  const renderToastContent = (toast: ToastWithVisibility) => {
    return (
      <ToastContent
        message={toast.message}
        message_type={toast.message_type}
        linkUrl={toast.linkUrl}
        linkLabel={toast.linkLabel}
      />
    );
  };

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast-${toast.message_type}${toast.visible ? ' toast--visible' : ''}`}
        >
          {renderToastContent(toast)}
        </div>
      ))}
    </div>
  );
};

export default Toast;

