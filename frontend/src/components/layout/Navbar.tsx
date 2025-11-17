import { Sun, Moon, Bell, Search, Menu, Settings, ChevronDown, Building2 } from 'lucide-react';
import { useUI } from '../../context/UIContext';
import { useAlerts } from '../../context/AlertContext';
import { useTenant } from '../../context/TenantContext';
import ProjectSwitcher from '../ProjectSwitcher';

export default function Navbar() {
  const { theme, toggleTheme, toggleSidebar } = useUI();
  const { getActiveAlerts } = useAlerts();
  const { currentTenant } = useTenant();

  const activeAlerts = getActiveAlerts();
  const criticalAlerts = activeAlerts.filter((a) => a.severity === 'critical').length;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0e1a] border-b border-[#1e293b] h-16">
      <div className="flex items-center justify-between h-full px-6">
        {/* Left side - Logo & Org Switcher */}
        <div className="flex items-center gap-6">
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-[#151b2b] rounded-lg transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-5 h-5 text-slate-400 hover:text-white" />
          </button>

          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-primary-600 via-primary-500 to-secondary-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-base">RA</span>
            </div>
            <div>
              <h1 className="text-base font-bold text-white tracking-tight">RAIA</h1>
              <p className="text-xs text-slate-500">AI Observability</p>
            </div>
          </div>

          <div className="h-8 w-px bg-[#1e293b]" />

          {/* Organization Switcher */}
          {currentTenant && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#151b2b] border border-[#1e293b] hover:border-[#334155] transition-colors cursor-pointer">
              <Building2 className="w-4 h-4 text-slate-400" />
              <span className="text-sm font-medium text-white">{currentTenant.name}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
            </div>
          )}

          <div className="h-8 w-px bg-[#1e293b]" />

          {/* Project Switcher */}
          <ProjectSwitcher />
        </div>

        {/* Center - Search */}
        <div className="hidden lg:flex flex-1 max-w-xl mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search evaluations, metrics, projects..."
              className="w-full pl-10 pr-4 py-2 bg-[#151b2b] border border-[#1e293b] rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-600 focus:ring-1 focus:ring-primary-600/50 transition-colors"
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-0.5 bg-[#0f172a] border border-[#1e293b] rounded text-xs text-slate-500 font-mono">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {/* Settings */}
          <button
            className="p-2 hover:bg-[#151b2b] rounded-lg transition-colors"
            aria-label="Settings"
          >
            <Settings className="w-5 h-5 text-slate-400 hover:text-white" />
          </button>

          {/* Notifications */}
          <button
            className="relative p-2 hover:bg-[#151b2b] rounded-lg transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5 text-slate-400 hover:text-white" />
            {criticalAlerts > 0 && (
              <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-critical-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-critical-500"></span>
              </span>
            )}
          </button>

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 hover:bg-[#151b2b] rounded-lg transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="w-5 h-5 text-slate-400 hover:text-white" />
            ) : (
              <Sun className="w-5 h-5 text-slate-400 hover:text-white" />
            )}
          </button>

          {/* User profile */}
          <div className="flex items-center gap-3 ml-2 pl-3 border-l border-[#1e293b]">
            <div className="flex items-center gap-2 cursor-pointer group">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-semibold">AB</span>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-400" />
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
