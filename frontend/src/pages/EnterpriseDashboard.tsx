/**
 * Enterprise Dashboard with Real-Time Updates
 * ===========================================
 * Shows real-time metrics, event ingestion stats, and system health
 * Uses WebSocket for live updates (no polling!)
 */

import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import {
  Activity,
  TrendingUp,
  AlertTriangle,
  Database,
  Zap,
  CheckCircle,
  Users,
  Server,
  Clock,
  BarChart3,
  HelpCircle,
  Info,
} from 'lucide-react';

// Tooltip component for help text
function Tooltip({ children, text }: { children: React.ReactNode; text: string }) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className="cursor-help"
      >
        {children}
      </div>
      {show && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-dark-900 border border-dark-700 rounded-lg shadow-xl max-w-xs">
          <p className="text-xs text-slate-300">{text}</p>
        </div>
      )}
    </div>
  );
}
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function EnterpriseDashboard() {
  const [realtimeMetrics, setRealtimeMetrics] = useState<any>(null);
  const [eventCount, setEventCount] = useState(0);

  // Fetch initial dashboard metrics
  const { data: dashboardMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => api.getDashboardMetrics({ time_range: '24h' }),
    refetchInterval: 60000, // Fallback polling every 60 seconds
  });

  // Fetch event stats
  const { data: eventStats, isLoading: statsLoading } = useQuery({
    queryKey: ['event-stats'],
    queryFn: () => api.getEventStats(),
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Fetch recent runs
  const { data: runsData, isLoading: runsLoading } = useQuery({
    queryKey: ['recent-runs'],
    queryFn: () => api.getRecentRuns({ limit: 10 }),
    refetchInterval: 30000,
  });

  // Real-time WebSocket connection
  const { isConnected, lastMessage, subscribe } = useWebSocket({
    onMessage: (message) => {
      console.log('WebSocket message:', message);

      if (message.type === 'metrics_update') {
        setRealtimeMetrics(message.data);
      }

      if (message.type === 'new_event') {
        setEventCount((prev) => prev + 1);
      }

      if (message.type === 'dashboard_update') {
        setRealtimeMetrics(message.data);
      }
    },
    onConnect: () => {
      console.log('✓ WebSocket connected to RAIA backend');
      // Subscribe to channels
      subscribe('dashboard');
      subscribe('metrics');
      subscribe('events');
    },
  });

  // Merge real-time metrics with fetched metrics
  const metrics = realtimeMetrics || dashboardMetrics;

  if (metricsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500 mx-auto mb-4" />
          <p className="text-slate-400">Loading Enterprise Dashboard...</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const eventTypeData = eventStats?.events_by_type
    ? Object.entries(eventStats.events_by_type).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value,
      }))
    : [];

  const tenantData = eventStats?.top_tenants
    ? Object.entries(eventStats.top_tenants).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <div className="space-y-6 p-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            Enterprise Dashboard
            <Tooltip text="Real-time monitoring of your RAG system's performance across all metrics. Track quality (precision, faithfulness), system health (events, runs), and user activity. The green 'Live' indicator shows you're receiving real-time updates via WebSocket - no refresh needed!">
              <HelpCircle className="w-5 h-5 text-slate-400" />
            </Tooltip>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time monitoring and analytics
            {isConnected && (
              <span className="ml-2 inline-flex items-center">
                <span className="h-2 w-2 bg-green-500 rounded-full animate-pulse mr-1" />
                <span className="text-green-400 text-xs">Live</span>
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs text-slate-500">System Status</div>
            <div className={`text-sm font-semibold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>
      </div>

      {/* Hero Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Runs */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-slate-400 text-sm mb-1 flex items-center gap-2">
                Total Runs
                <Tooltip text="Total number of RAG queries executed across your system. Each run represents one complete query-to-answer cycle. Increasing runs indicate growing system usage and user engagement.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="text-3xl font-bold text-white">
                {metrics?.total_runs?.toLocaleString() || 0}
              </div>
              <div className="text-green-400 text-sm mt-2 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1" />
                +12% from yesterday
              </div>
            </div>
            <div className="p-3 bg-primary-500/10 rounded-lg">
              <Activity className="w-6 h-6 text-primary-500" />
            </div>
          </div>
        </div>

        {/* Events Ingested */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-slate-400 text-sm mb-1 flex items-center gap-2">
                Events Ingested
                <Tooltip text="Total number of evaluation events captured by the system. Events include runs, attributions, reasoning traces, and metrics. Higher event rates indicate active monitoring and comprehensive data collection. Events/min shows real-time ingestion rate.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="text-3xl font-bold text-white">
                {(eventStats?.total_events || 0).toLocaleString()}
              </div>
              <div className="text-slate-400 text-sm mt-2">
                {eventStats?.events_per_minute_last_hour?.toFixed(1) || 0} events/min
              </div>
            </div>
            <div className="p-3 bg-success-500/10 rounded-lg">
              <Database className="w-6 h-6 text-success-500" />
            </div>
          </div>
        </div>

        {/* Avg Precision */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-slate-400 text-sm mb-1 flex items-center gap-2">
                Avg Precision
                <Tooltip text="Precision measures what percentage of retrieved documents were relevant. High precision (>80%) means your retrieval is accurate - most documents you retrieve are useful. Low precision means you're retrieving too many irrelevant documents. Recall shows what percentage of all relevant documents you successfully retrieved.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="text-3xl font-bold text-white">
                {((metrics?.avg_precision || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-slate-400 text-sm mt-2">
                Recall: {((metrics?.avg_recall || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-3 bg-warning-500/10 rounded-lg">
              <BarChart3 className="w-6 h-6 text-warning-500" />
            </div>
          </div>
        </div>

        {/* Avg Faithfulness */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-slate-400 text-sm mb-1 flex items-center gap-2">
                Avg Faithfulness
                <Tooltip text="Faithfulness measures how well your answers stick to the source documents. High faithfulness (&gt;90%) means answers are grounded in retrieved content with minimal hallucination. Low faithfulness indicates the model is making things up or adding information not present in sources. Hallucination percentage shows the inverse - lower is better.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="text-3xl font-bold text-white">
                {((metrics?.avg_faithfulness || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-slate-400 text-sm mt-2">
                Hallucination: {((metrics?.avg_hallucination || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-3 bg-critical-500/10 rounded-lg">
              <CheckCircle className="w-6 h-6 text-critical-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Event Types Distribution */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            Event Types Distribution
            <Tooltip text="Breakdown of different event types ingested by the system. Shows the distribution of runs, attributions, reasoning traces, drift detections, and other evaluation events. Helps you understand what types of data your system is collecting most.">
              <HelpCircle className="w-4 h-4 text-slate-400" />
            </Tooltip>
          </h3>
          {eventTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={eventTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {eventTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-300 flex items-center justify-center text-slate-400">
              No event data available
            </div>
          )}
        </div>

        {/* Top Tenants */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            Top Tenants by Events
            <Tooltip text="Top users or organizations generating the most events. In multi-tenant RAG systems, this shows which tenants are most active. Useful for understanding usage patterns, capacity planning, and identifying power users who may need additional support or resources.">
              <HelpCircle className="w-4 h-4 text-slate-400" />
            </Tooltip>
          </h3>
          {tenantData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tenantData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-slate-400">
              No tenant data available
            </div>
          )}
        </div>
      </div>

      {/* Recent Runs Table */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          Recent Runs
          <Tooltip text="Latest RAG query executions with key metrics. Shows run ID, query text, agent used, precision score, and faithfulness score. Use this to quickly spot performance issues, track query patterns, and monitor answer quality in real-time.">
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </Tooltip>
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left text-slate-400 text-sm font-medium p-3">Run ID</th>
                <th className="text-left text-slate-400 text-sm font-medium p-3">Query</th>
                <th className="text-left text-slate-400 text-sm font-medium p-3">Agent</th>
                <th className="text-right text-slate-400 text-sm font-medium p-3">Precision</th>
                <th className="text-right text-slate-400 text-sm font-medium p-3">Faithfulness</th>
                <th className="text-left text-slate-400 text-sm font-medium p-3">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {runsData?.runs?.slice(0, 10).map((run: any) => (
                <tr key={run.run_id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="p-3 text-sm text-slate-300 font-mono">
                    {run.run_id.substring(0, 8)}...
                  </td>
                  <td className="p-3 text-sm text-white max-w-md truncate">
                    {run.query || 'N/A'}
                  </td>
                  <td className="p-3 text-sm text-slate-300">{run.agent_id || 'Unknown'}</td>
                  <td className="p-3 text-sm text-right">
                    <span className="text-primary-400">
                      {run.precision ? (run.precision * 100).toFixed(1) + '%' : 'N/A'}
                    </span>
                  </td>
                  <td className="p-3 text-sm text-right">
                    <span className="text-success-400">
                      {run.faithfulness ? (run.faithfulness * 100).toFixed(1) + '%' : 'N/A'}
                    </span>
                  </td>
                  <td className="p-3 text-sm text-slate-400">
                    {run.timestamp ? new Date(run.timestamp).toLocaleString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {(!runsData || runsData.runs?.length === 0) && (
            <div className="text-center py-8 text-slate-400">
              No recent runs available. Start sending events from your agentic AI!
            </div>
          )}
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-sm">WebSocket Status</div>
              <div className={`text-lg font-semibold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>
            <Server className={`w-8 h-8 ${isConnected ? 'text-green-500' : 'text-red-500'}`} />
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-sm">Active Sessions</div>
              <div className="text-lg font-semibold text-white">
                {metrics?.total_sessions || 0}
              </div>
            </div>
            <Users className="w-8 h-8 text-primary-500" />
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-sm">Active Agents</div>
              <div className="text-lg font-semibold text-white">{metrics?.total_agents || 0}</div>
            </div>
            <Zap className="w-8 h-8 text-warning-500" />
          </div>
        </div>
      </div>
    </div>
  );
}
