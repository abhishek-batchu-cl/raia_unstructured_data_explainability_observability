import type { Tenant, Project, DataSource } from '../types';

export const mockTenants: Tenant[] = [
  {
    id: 'tenant-1',
    name: 'Acme Corporation',
    slug: 'acme-corp',
    logo: 'https://ui-avatars.com/api/?name=Acme+Corp&background=6366f1&color=fff',
    createdAt: '2024-01-15T10:00:00Z',
    plan: 'enterprise',
    members: 45,
  },
  {
    id: 'tenant-2',
    name: 'TechStart Inc',
    slug: 'techstart',
    logo: 'https://ui-avatars.com/api/?name=TechStart&background=8b5cf6&color=fff',
    createdAt: '2024-03-20T14:30:00Z',
    plan: 'pro',
    members: 12,
  },
];

export const mockDataSources: DataSource[] = [
  {
    id: 'ds-1',
    type: 's3',
    name: 'Production Logs - AWS S3',
    status: 'connected',
    connectedAt: '2024-09-01T10:00:00Z',
    lastSync: '2025-10-18T15:30:00Z',
    config: {
      bucket: 'raia-prod-logs',
      region: 'us-east-1',
      prefix: 'logs/agent-interactions/',
    },
  },
  {
    id: 'ds-2',
    type: 'api',
    name: 'Real-time API Stream',
    status: 'connected',
    connectedAt: '2024-09-15T12:00:00Z',
    lastSync: '2025-10-18T15:35:00Z',
    config: {
      endpoint: 'https://api.example.com/agent-metrics',
      authType: 'bearer',
    },
  },
  {
    id: 'ds-3',
    type: 'sdk',
    name: 'Python SDK Integration',
    status: 'connected',
    connectedAt: '2024-10-01T08:00:00Z',
    lastSync: '2025-10-18T15:32:00Z',
    config: {
      version: '2.1.0',
      language: 'python',
    },
  },
];

export const mockProjects: Project[] = [
  {
    id: 'proj-1',
    tenantId: 'tenant-1',
    name: 'Customer Support Agent',
    description: 'AI-powered customer support agent handling 10K+ queries daily',
    type: 'agentic-ai',
    createdAt: '2024-08-15T10:00:00Z',
    updatedAt: '2025-10-18T15:00:00Z',
    dataSources: [mockDataSources[0], mockDataSources[1]],
    evaluationCount: 1247,
    status: 'active',
    tags: ['production', 'customer-facing', 'high-priority'],
    team: ['john@acme.com', 'sarah@acme.com', 'mike@acme.com'],
  },
  {
    id: 'proj-2',
    tenantId: 'tenant-1',
    name: 'Document Q&A RAG',
    description: 'RAG pipeline for internal documentation and knowledge base',
    type: 'rag-pipeline',
    createdAt: '2024-09-01T14:00:00Z',
    updatedAt: '2025-10-17T09:00:00Z',
    dataSources: [mockDataSources[2]],
    evaluationCount: 543,
    status: 'active',
    tags: ['internal', 'knowledge-base'],
    team: ['alice@acme.com', 'bob@acme.com'],
  },
  {
    id: 'proj-3',
    tenantId: 'tenant-1',
    name: 'Sales Assistant Bot',
    description: 'Conversational AI for sales enablement and lead qualification',
    type: 'chatbot',
    createdAt: '2024-07-20T11:00:00Z',
    updatedAt: '2025-10-16T16:00:00Z',
    dataSources: [mockDataSources[0]],
    evaluationCount: 892,
    status: 'active',
    tags: ['sales', 'lead-generation'],
    team: ['emma@acme.com', 'david@acme.com'],
  },
  {
    id: 'proj-4',
    tenantId: 'tenant-1',
    name: 'Code Review Assistant',
    description: 'AI agent for automated code review and suggestions',
    type: 'llm-application',
    createdAt: '2024-06-10T08:00:00Z',
    updatedAt: '2025-10-15T12:00:00Z',
    dataSources: [],
    evaluationCount: 156,
    status: 'paused',
    tags: ['development', 'internal'],
    team: ['frank@acme.com'],
  },
  {
    id: 'proj-5',
    tenantId: 'tenant-2',
    name: 'Healthcare Chatbot',
    description: 'HIPAA-compliant patient engagement chatbot',
    type: 'chatbot',
    createdAt: '2024-04-01T10:00:00Z',
    updatedAt: '2025-10-18T14:00:00Z',
    dataSources: [
      {
        id: 'ds-4',
        type: 'azure-blob',
        name: 'Azure Blob Storage',
        status: 'connected',
        connectedAt: '2024-04-05T10:00:00Z',
        lastSync: '2025-10-18T14:30:00Z',
        config: {
          container: 'healthcare-logs',
          accountName: 'techstart-storage',
        },
      },
    ],
    evaluationCount: 734,
    status: 'active',
    tags: ['healthcare', 'hipaa', 'compliance'],
    team: ['lisa@techstart.com', 'mark@techstart.com'],
  },
];

// Helper function to get projects by tenant
export const getProjectsByTenant = (tenantId: string): Project[] => {
  return mockProjects.filter((p) => p.tenantId === tenantId);
};

// Helper function to get active projects
export const getActiveProjects = (tenantId: string): Project[] => {
  return mockProjects.filter((p) => p.tenantId === tenantId && p.status === 'active');
};
