import { createContext, useContext, useState, ReactNode } from 'react';
import type { Alert } from '../types';
import { mockEvaluations } from '../data/mockData';

interface AlertContextType {
  alerts: Alert[];
  dismissedAlerts: string[];
  addAlert: (alert: Alert) => void;
  dismissAlert: (id: string) => void;
  clearAlerts: () => void;
  getActiveAlerts: () => Alert[];
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export function AlertProvider({ children }: { children: ReactNode }) {
  const [alerts, setAlerts] = useState<Alert[]>(mockEvaluations[0]?.alerts || []);
  const [dismissedAlerts, setDismissedAlerts] = useState<string[]>([]);

  const addAlert = (alert: Alert) => {
    setAlerts(prev => [...prev, alert]);
  };

  const dismissAlert = (id: string) => {
    setDismissedAlerts(prev => [...prev, id]);
  };

  const clearAlerts = () => {
    setAlerts([]);
    setDismissedAlerts([]);
  };

  const getActiveAlerts = () => {
    return alerts.filter(alert => !dismissedAlerts.includes(alert.id));
  };

  return (
    <AlertContext.Provider value={{ alerts, dismissedAlerts, addAlert, dismissAlert, clearAlerts, getActiveAlerts }}>
      {children}
    </AlertContext.Provider>
  );
}

export function useAlerts() {
  const context = useContext(AlertContext);
  if (context === undefined) {
    throw new Error('useAlerts must be used within an AlertProvider');
  }
  return context;
}
