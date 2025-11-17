import { create } from 'zustand';
import type { Evaluation, FilterState } from '../types';
import { mockEvaluations } from '../data/mockData';

interface EvaluationStore {
  evaluations: Evaluation[];
  selectedEvaluation: Evaluation | null;
  filters: FilterState;
  setEvaluations: (evaluations: Evaluation[]) => void;
  selectEvaluation: (id: string) => void;
  updateFilters: (filters: Partial<FilterState>) => void;
  getFilteredEvaluations: () => Evaluation[];
  compareEvaluations: (ids: string[]) => Evaluation[];
}

export const useEvaluationStore = create<EvaluationStore>((set, get) => ({
  evaluations: mockEvaluations,
  selectedEvaluation: null,
  filters: {
    agentVersions: [],
    categories: [],
  },

  setEvaluations: (evaluations) => set({ evaluations }),

  selectEvaluation: (id) => {
    const evaluation = get().evaluations.find((e) => e.id === id);
    set({ selectedEvaluation: evaluation || null });
  },

  updateFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),

  getFilteredEvaluations: () => {
    const { evaluations, filters } = get();

    return evaluations.filter((evaluation) => {
      // Filter by date range
      if (filters.dateRange) {
        const { from, to } = filters.dateRange;
        const evalDate = new Date(evaluation.timestamp);
        if (evalDate < from || evalDate > to) return false;
      }

      // Filter by agent versions
      if (filters.agentVersions.length > 0) {
        if (!filters.agentVersions.includes(evaluation.agentVersion)) return false;
      }

      // Filter by score range
      if (filters.scoreRange) {
        const { min, max } = filters.scoreRange;
        if (evaluation.overallScore < min || evaluation.overallScore > max) return false;
      }

      // Filter by search query
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        const matchesId = evaluation.id.toLowerCase().includes(query);
        const matchesVersion = evaluation.agentVersion.toLowerCase().includes(query);
        if (!matchesId && !matchesVersion) return false;
      }

      return true;
    });
  },

  compareEvaluations: (ids) => {
    const { evaluations } = get();
    return evaluations.filter((e) => ids.includes(e.id));
  },
}));
