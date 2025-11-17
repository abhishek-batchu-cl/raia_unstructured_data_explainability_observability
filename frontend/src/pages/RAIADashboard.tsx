import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  TrendingUp,
  AlertTriangle,
  Database,
  Zap,
  CheckCircle,
  Brain,
  Link2,
  GitBranch,
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../services/api';
import type { DashboardSummary } from '../services/api';

export default function RAIADashboard() {
  // Fetch real dashboard data from API
  const { data: summary, isLoading, error } = useQuery<DashboardSummary>({
    queryKey: ['dashboard'],
    queryFn: () => api.getDashboard(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch timeseries data for faithfulness
  const { data: timeseriesData = [] } = useQuery({
    queryKey: ['timeseries', 'faithfulness'],
    queryFn: () => api.getTimeseries({ metric_name: 'faithfulness', hours: 24 }),
  });

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-critical-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Failed to Load Dashboard</h2>
          <p className="text-slate-400 mb-4">Could not connect to RAIA backend API</p>
          <p className="text-sm text-slate-500">
            Make sure the backend is running on http://localhost:8000
          </p>
        </div>
      </div>
    );
  }

  if (isLoading || !summary) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500 mx-auto mb-4" />
          <p className="text-slate-400">Loading RAIA dashboard...</p>
        </div>
      </div>
    );
  }

  // Calculate derived metrics
  const overallScore =
    ((summary.avg_faithfulness + summary.avg_precision + summary.avg_recall) / 3) * 100;
  const ragHealthScore = ((summary.avg_precision + summary.avg_recall) / 2) * 100;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">RAIA Enterprise Dashboard</h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Real-time RAG evaluation and monitoring • Powered by FastAPI
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary">
            <Database className="w-4 h-4 mr-2 inline" />
            Data Sources
          </button>
          <button className="btn-primary">
            <Activity className="w-4 h-4 mr-2 inline" />
            New Evaluation
          </button>
        </div>
      </div>

      {/* Hero Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Runs */}
        <div className="card p-6 border border-primary-500/20 bg-gradient-to-br from-primary-500/5 to-transparent">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Total Evaluations
              </p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{summary.total_runs}</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">RAG pipeline executions</span>
          </div>
        </div>

        {/* Faithfulness */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Avg Faithfulness
              </p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">
                  {(summary.avg_faithfulness * 100).toFixed(1)}
                </span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">
              Hallucination: {(summary.avg_hallucination * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {/* RAG Precision & Recall */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                RAG Health
              </p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-primary-500">
                  {ragHealthScore.toFixed(1)}
                </span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Database className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">
              P: {(summary.avg_precision * 100).toFixed(1)}% • R:{' '}
              {(summary.avg_recall * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Avg Latency */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Avg Latency
              </p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">
                  {summary.avg_latency_ms.toFixed(0)}
                </span>
                <span className="text-slate-500 text-sm">ms</span>
              </div>
            </div>
            <div className="p-2 bg-warning-500/20 rounded-lg">
              <Zap className="w-6 h-6 text-warning-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Response time</span>
          </div>
        </div>
      </div>

      {/* RAIA Features Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Attributions */}
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Link2 className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Attribution Mappings</h3>
              <p className="text-xs text-slate-500">Answer-source tracing</p>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{summary.total_attributions}</span>
            <span className="text-sm text-slate-400">total</span>
          </div>
        </div>

        {/* Reasoning Traces */}
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-success-500/20 rounded-lg">
              <Brain className="w-5 h-5 text-success-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Reasoning Traces</h3>
              <p className="text-xs text-slate-500">Step-by-step execution</p>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">
              {summary.total_reasoning_traces}
            </span>
            <span className="text-sm text-slate-400">traces</span>
          </div>
        </div>

        {/* Drift Detection */}
        <div
          className={`card p-5 ${
            summary.drift_detected ? 'border border-critical-500/30' : ''
          }`}
        >
          <div className="flex items-center gap-3 mb-3">
            <div
              className={`p-2 rounded-lg ${
                summary.drift_detected ? 'bg-critical-500/20' : 'bg-slate-500/20'
              }`}
            >
              <GitBranch
                className={`w-5 h-5 ${
                  summary.drift_detected ? 'text-critical-400' : 'text-slate-400'
                }`}
              />
            </div>
            <div>
              <h3 className="font-semibold text-white">Drift Detection</h3>
              <p className="text-xs text-slate-500">Embedding stability</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {summary.drift_detected ? (
              <>
                <AlertTriangle className="w-5 h-5 text-critical-500" />
                <span className="text-sm font-medium text-critical-400">DRIFT DETECTED</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5 text-success-500" />
                <span className="text-sm font-medium text-success-400">STABLE</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Faithfulness Trend Chart */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">Faithfulness Trend (24h)</h2>
            <p className="text-sm text-slate-400 mt-1">Real-time metric tracking</p>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeseriesData}>
            <defs>
              <linearGradient id="faithfulness" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="timestamp"
              stroke="#64748b"
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis
              stroke="#64748b"
              domain={[0, 1]}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '8px',
              }}
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value: any) => `${(value * 100).toFixed(2)}%`}
            />
            <Line
              type="monotone"
              dataKey="value"
              name="Faithfulness"
              stroke="#10b981"
              strokeWidth={3}
              dot={{ fill: '#10b981', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <a
          href="/attribution"
          className="card p-5 hover:border-primary-500/30 transition-all cursor-pointer group"
        >
          <Link2 className="w-8 h-8 text-primary-400 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-white mb-1">Attribution</h3>
          <p className="text-sm text-slate-400">View answer-source mappings →</p>
        </a>

        <a
          href="/reasoning"
          className="card p-5 hover:border-success-500/30 transition-all cursor-pointer group"
        >
          <Brain className="w-8 h-8 text-success-400 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-white mb-1">Reasoning</h3>
          <p className="text-sm text-slate-400">Explore reasoning traces →</p>
        </a>

        <a
          href="/monitoring"
          className="card p-5 hover:border-warning-500/30 transition-all cursor-pointer group"
        >
          <Activity className="w-8 h-8 text-warning-400 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-white mb-1">Monitoring</h3>
          <p className="text-sm text-slate-400">System health & drift →</p>
        </a>

        <a
          href="/whatif"
          className="card p-5 hover:border-purple-500/30 transition-all cursor-pointer group"
        >
          <Zap className="w-8 h-8 text-purple-400 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-white mb-1">What-If</h3>
          <p className="text-sm text-slate-400">Optimization insights →</p>
        </a>
      </div>
    </div>
  );
}
