import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, Plus, FolderKanban, Database } from 'lucide-react';
import { useTenant } from '../context/TenantContext';
import type { Project } from '../types';

export default function ProjectSwitcher() {
  const { currentProject, projects, switchProject } = useTenant();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.addEventListener('removeEventListener', handleClickOutside);
  }, []);

  const getProjectTypeIcon = (type: Project['type']) => {
    return <FolderKanban className="w-4 h-4" />;
  };

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'bg-success-500';
      case 'paused':
        return 'bg-warning-500';
      case 'archived':
        return 'bg-slate-500';
      default:
        return 'bg-slate-500';
    }
  };

  if (!currentProject) {
    return (
      <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors">
        <Plus className="w-4 h-4" />
        <span>Create Project</span>
      </button>
    );
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#151b2b] border border-[#1e293b] hover:border-[#334155] transition-colors min-w-[200px] text-left"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {getProjectTypeIcon(currentProject.type)}
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white truncate">{currentProject.name}</div>
            <div className="text-xs text-slate-400 truncate">{currentProject.type.replace('-', ' ')}</div>
          </div>
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-[#151b2b] border border-[#1e293b] rounded-lg shadow-2xl overflow-hidden z-50">
          <div className="p-2 border-b border-[#1e293b]">
            <input
              type="text"
              placeholder="Search projects..."
              className="w-full px-3 py-2 text-sm bg-[#0f172a] border border-[#1e293b] rounded-md text-white placeholder-slate-500 focus:outline-none focus:border-primary-600"
            />
          </div>

          <div className="max-h-[400px] overflow-y-auto">
            {/* Active Projects */}
            <div className="p-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-2 py-1">
                Active Projects
              </div>
              {projects
                .filter((p) => p.status === 'active')
                .map((project) => (
                  <button
                    key={project.id}
                    onClick={() => {
                      switchProject(project.id);
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-2 py-2 rounded-md hover:bg-[#1e293b] transition-colors text-left group"
                  >
                    <div className="flex-shrink-0">
                      {getProjectTypeIcon(project.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white truncate">{project.name}</span>
                        <div className={`w-1.5 h-1.5 rounded-full ${getStatusColor(project.status)}`} />
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-slate-400">{project.evaluationCount} evaluations</span>
                        {project.dataSources.length > 0 && (
                          <>
                            <span className="text-xs text-slate-600">•</span>
                            <div className="flex items-center gap-1 text-xs text-slate-400">
                              <Database className="w-3 h-3" />
                              <span>{project.dataSources.length} sources</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                    {currentProject.id === project.id && (
                      <Check className="w-4 h-4 text-primary-500 flex-shrink-0" />
                    )}
                  </button>
                ))}
            </div>

            {/* Paused Projects */}
            {projects.filter((p) => p.status === 'paused').length > 0 && (
              <div className="p-2 border-t border-[#1e293b]">
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-2 py-1">
                  Paused Projects
                </div>
                {projects
                  .filter((p) => p.status === 'paused')
                  .map((project) => (
                    <button
                      key={project.id}
                      onClick={() => {
                        switchProject(project.id);
                        setIsOpen(false);
                      }}
                      className="w-full flex items-center gap-3 px-2 py-2 rounded-md hover:bg-[#1e293b] transition-colors text-left opacity-60 hover:opacity-100"
                    >
                      <div className="flex-shrink-0">
                        {getProjectTypeIcon(project.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-white truncate">{project.name}</span>
                          <div className={`w-1.5 h-1.5 rounded-full ${getStatusColor(project.status)}`} />
                        </div>
                        <span className="text-xs text-slate-400">{project.evaluationCount} evaluations</span>
                      </div>
                      {currentProject.id === project.id && (
                        <Check className="w-4 h-4 text-primary-500 flex-shrink-0" />
                      )}
                    </button>
                  ))}
              </div>
            )}
          </div>

          <div className="p-2 border-t border-[#1e293b]">
            <button className="w-full flex items-center gap-2 px-2 py-2 text-sm font-medium text-primary-400 hover:text-primary-300 hover:bg-[#1e293b] rounded-md transition-colors">
              <Plus className="w-4 h-4" />
              <span>Create New Project</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
