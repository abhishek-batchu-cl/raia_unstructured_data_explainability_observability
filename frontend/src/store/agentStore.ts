import { create } from 'zustand';
import type { Agent } from '../types';
import { mockAgents } from '../data/mockData';

interface AgentStore {
  agents: Agent[];
  selectedAgents: Agent[];
  selectAgent: (agent: Agent) => void;
  deselectAgent: (agentId: string) => void;
  clearSelectedAgents: () => void;
  getAgentById: (id: string) => Agent | undefined;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: mockAgents,
  selectedAgents: [],

  selectAgent: (agent) => {
    const { selectedAgents } = get();
    // Limit to 4 agents for comparison
    if (selectedAgents.length >= 4) {
      return;
    }
    if (!selectedAgents.find((a) => a.id === agent.id)) {
      set({ selectedAgents: [...selectedAgents, agent] });
    }
  },

  deselectAgent: (agentId) => {
    set((state) => ({
      selectedAgents: state.selectedAgents.filter((a) => a.id !== agentId),
    }));
  },

  clearSelectedAgents: () => set({ selectedAgents: [] }),

  getAgentById: (id) => {
    return get().agents.find((a) => a.id === id);
  },
}));
