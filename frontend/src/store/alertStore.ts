import { create } from 'zustand';
import type { Alert } from '../types';
import { mockEvaluations } from '../data/mockData';

interface AlertStore {
  alerts: Alert[];
  dismissedAlerts: string[];
  addAlert: (alert: Alert) => void;
  dismissAlert: (id: string) => void;
  clearAlerts: () => void;
}

export const useAlertStore = create<AlertStore>((set) => ({
  // Initialize with alerts from the latest evaluation
  alerts: mockEvaluations[0]?.alerts || [],
  dismissedAlerts: [],

  addAlert: (alert) =>
    set((state) => ({
      alerts: [...state.alerts, alert],
    })),

  dismissAlert: (id) =>
    set((state) => ({
      dismissedAlerts: [...state.dismissedAlerts, id],
    })),

  clearAlerts: () => set({ alerts: [], dismissedAlerts: [] }),
}));
