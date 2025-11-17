import { NavLink } from 'react-router-dom';
import {
  Home,
  FileText,
  Zap,
  Shield,
  AlertTriangle,
  Users,
  CheckCircle,
  History,
  GitCompare,
  FileBarChart,
  Activity,
  Link2,
  Brain,
  Lightbulb,
  BarChart3,
} from 'lucide-react';
import { useUI } from '../../context/UIContext';
import { cn } from '../../lib/utils';

const navItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  {
    path: '/enterprise',
    label: 'Enterprise Metrics',
    icon: BarChart3,
    category: 'Dashboards',
  },
  {
    path: '/output-quality',
    label: 'Output Quality',
    icon: FileText,
    category: 'Metrics',
  },
  { path: '/performance', label: 'Performance', icon: Zap },
  { path: '/robustness', label: 'Robustness', icon: Shield },
  { path: '/safety', label: 'Safety & Ethics', icon: AlertTriangle },
  { path: '/user-experience', label: 'User Experience', icon: Users },
  { path: '/compliance', label: 'Compliance', icon: CheckCircle },
  {
    path: '/attribution',
    label: 'Attribution',
    icon: Link2,
    category: 'RAIA Explainability',
  },
  { path: '/reasoning', label: 'Reasoning Traces', icon: Brain },
  { path: '/monitoring', label: 'System Monitoring', icon: Activity },
  { path: '/whatif', label: 'What-If Analysis', icon: Lightbulb },
  {
    path: '/history',
    label: 'Evaluation History',
    icon: History,
    category: 'Analysis',
  },
  { path: '/compare', label: 'Compare Agents', icon: GitCompare },
  { path: '/reports', label: 'Reports & Export', icon: FileBarChart },
];

export default function Sidebar() {
  const { sidebarCollapsed } = useUI();

  return (
    <aside
      className={cn(
        'fixed left-0 top-16 h-[calc(100vh-4rem)] bg-[#0f172a] border-r border-[#1e293b] transition-all duration-300 overflow-y-auto',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      <nav className="p-3 space-y-0.5">
        {navItems.map((item, index) => {
          const showCategoryLabel =
            item.category &&
            (index === 0 || navItems[index - 1].category !== item.category);

          return (
            <div key={item.path}>
              {showCategoryLabel && !sidebarCollapsed && (
                <div className="px-3 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mt-4 first:mt-0">
                  {item.category}
                </div>
              )}
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group',
                    isActive
                      ? 'bg-primary-600/10 text-primary-400 border-l-2 border-primary-500'
                      : 'text-slate-400 hover:bg-dark-850 hover:text-white border-l-2 border-transparent'
                  )
                }
                title={sidebarCollapsed ? item.label : undefined}
                onClick={(e) => {
                  // Prevent opening in new tab on middle-click or cmd/ctrl-click
                  if (e.button === 1 || e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                  }
                }}
                onAuxClick={(e) => {
                  // Prevent middle-click from opening new tab
                  e.preventDefault();
                }}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && (
                  <span className="text-sm font-medium truncate">{item.label}</span>
                )}
              </NavLink>
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
