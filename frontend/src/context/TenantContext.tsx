import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import type { Tenant, Project } from '../types';
import { mockTenants, mockProjects, getProjectsByTenant } from '../data/mockTenants';

interface TenantContextType {
  currentTenant: Tenant | null;
  currentProject: Project | null;
  tenants: Tenant[];
  projects: Project[];
  setCurrentTenant: (tenant: Tenant) => void;
  setCurrentProject: (project: Project | null) => void;
  switchTenant: (tenantId: string) => void;
  switchProject: (projectId: string) => void;
}

const TenantContext = createContext<TenantContextType | undefined>(undefined);

export function TenantProvider({ children }: { children: ReactNode }) {
  const [tenants] = useState<Tenant[]>(mockTenants);
  const [currentTenant, setCurrentTenant] = useState<Tenant | null>(mockTenants[0]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);

  // Update projects when tenant changes
  useEffect(() => {
    if (currentTenant) {
      const tenantProjects = getProjectsByTenant(currentTenant.id);
      setProjects(tenantProjects);
      // Auto-select first active project
      const firstActive = tenantProjects.find((p) => p.status === 'active');
      setCurrentProject(firstActive || tenantProjects[0] || null);
    } else {
      setProjects([]);
      setCurrentProject(null);
    }
  }, [currentTenant]);

  const switchTenant = (tenantId: string) => {
    const tenant = tenants.find((t) => t.id === tenantId);
    if (tenant) {
      setCurrentTenant(tenant);
    }
  };

  const switchProject = (projectId: string) => {
    const project = projects.find((p) => p.id === projectId);
    if (project) {
      setCurrentProject(project);
    }
  };

  return (
    <TenantContext.Provider
      value={{
        currentTenant,
        currentProject,
        tenants,
        projects,
        setCurrentTenant,
        setCurrentProject,
        switchTenant,
        switchProject,
      }}
    >
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);
  if (context === undefined) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
}
