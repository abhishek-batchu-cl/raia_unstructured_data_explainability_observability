import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  History as HistoryIcon,
  Calendar,
  Filter,
  Download,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  HelpCircle,
  Info,
  Search,
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { api } from '../services/api';

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

export default function History() {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | '90d'>('7d');
  const [filterAgent, setFilterAgent] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch recent runs
  const { data: runsData, isLoading: runsLoading } = useQuery({
    queryKey: ['recent-runs', timeRange],
    queryFn: () => api.getRecentRuns({ limit: 100 }),
  });

  // Fetch time series data for trends
  const { data: timeseriesData, isLoading: timeseriesLoading } = useQuery({
    queryKey: ['timeseries', timeRange],
    queryFn: () =>
      api.getTimeseries({
        metric: 'precision',
        start_time: getStartTime(timeRange),
        end_time: new Date().toISOString(),
        granularity: timeRange === '24h' ? 'hour' : 'day',
      }),
  });

  const runs = useMemo(() => {
    if (!runsData?.runs) return [];

    let filtered = runsData.runs;

    // Filter by agent
    if (filterAgent !== 'all') {
      filtered = filtered.filter((r) => r.agent_id === filterAgent);
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (r) =>
          r.run_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.query?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.agent_id.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filtered;
  }, [runsData, filterAgent, searchQuery]);

  // Get unique agents for filter dropdown
  const uniqueAgents = useMemo(() => {
    if (!runsData?.runs) return [];
    return [...new Set(runsData.runs.map((r) => r.agent_id))];
  }, [runsData]);

  // Calculate summary statistics
  const stats = useMemo(() => {
    if (runs.length === 0)
      return { total: 0, avgPrecision: 0, avgFaithfulness: 0, successRate: 0 };

    const total = runs.length;
    const avgPrecision =
      runs.reduce((acc, r) => acc + (r.precision || 0), 0) / total;
    const avgFaithfulness =
      runs.reduce((acc, r) => acc + (r.faithfulness || 0), 0) / total;
    const successful = runs.filter((r) => r.precision && r.precision > 0.7).length;
    const successRate = (successful / total) * 100;

    return { total, avgPrecision, avgFaithfulness, successRate };
  }, [runs]);

  // Prepare trend data
  const trendData = useMemo(() => {
    if (!timeseriesData?.data) return [];
    return timeseriesData.data.map((d: any) => ({
      timestamp: new Date(d.timestamp).toLocaleDateString(),
      value: d.value,
    }));
  }, [timeseriesData]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            Evaluation History
            <Tooltip text="Complete timeline of all evaluation runs with trends, filters, and drill-down capabilities. Track how your RAG system's performance changes over time, identify patterns, and compare different time periods to understand system evolution.">
              <HelpCircle className="w-5 h-5 text-slate-400" />
            </Tooltip>
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Historical evaluation data and performance trends
          </p>
        </div>
        <button className="btn-primary">
          <Download className="w-4 h-4 mr-2 inline" />
          Export History
        </button>
      </div>

      {/* How Evaluation History Works */}
      <div className="card p-6 bg-primary-500/5 border-2 border-primary-500/30">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-primary-300">Understanding Evaluation History</h3>
            <p className="text-xs text-slate-400 mt-1">
              Evaluation History tracks every query your RAG system processes over time. Use this to:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-primary-400">•</span>
                <span><strong>Spot trends:</strong> See if precision/faithfulness is improving or degrading</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-400">•</span>
                <span><strong>Compare periods:</strong> How does performance today compare to last week?</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-400">•</span>
                <span><strong>Find anomalies:</strong> Identify sudden drops in quality or unusual patterns</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-400">•</span>
                <span><strong>Track changes:</strong> See the impact of configuration changes or model updates</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-6 border border-primary-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Total Runs
                </p>
                <Tooltip text="Total number of evaluation runs in the selected time period. Each run represents one query processed by your RAG system. More runs indicate higher system usage.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{stats.total}</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <HistoryIcon className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">In last {timeRange}</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg Precision
                </p>
                <Tooltip text="Average precision score across all runs in this period. Shows how accurately your system retrieves relevant documents. Values above 0.8 (80%) are excellent. Trending up means retrieval is improving.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">
                  {(stats.avgPrecision * 100).toFixed(1)}
                </span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Retrieval accuracy</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg Faithfulness
                </p>
                <Tooltip text="Average faithfulness score - how well answers stick to source documents. High values (&gt;0.9) mean minimal hallucination. Low values indicate the model is making things up. This is critical for RAG system trustworthiness.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">
                  {(stats.avgFaithfulness * 100).toFixed(1)}
                </span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Answer grounding</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Success Rate
                </p>
                <Tooltip text="Percentage of runs with precision &gt; 70%. This is your 'quality bar' - what percentage of queries meet acceptable standards. Track this to ensure system reliability doesn't degrade over time.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">
                  {stats.successRate.toFixed(1)}
                </span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Quality threshold</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-4 flex-wrap">
          {/* Time Range */}
          <div className="flex-1 min-w-[200px]">
            <label className="text-xs text-slate-400 block mb-1 flex items-center gap-2">
              <Calendar className="w-3.5 h-3.5" />
              Time Range
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-2"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>

          {/* Agent Filter */}
          <div className="flex-1 min-w-[200px]">
            <label className="text-xs text-slate-400 block mb-1 flex items-center gap-2">
              <Filter className="w-3.5 h-3.5" />
              Agent
            </label>
            <select
              value={filterAgent}
              onChange={(e) => setFilterAgent(e.target.value)}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-2"
            >
              <option value="all">All Agents</option>
              {uniqueAgents.map((agent) => (
                <option key={agent} value={agent}>
                  {agent}
                </option>
              ))}
            </select>
          </div>

          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <label className="text-xs text-slate-400 block mb-1 flex items-center gap-2">
              <Search className="w-3.5 h-3.5" />
              Search
            </label>
            <input
              type="text"
              placeholder="Search runs, queries, agents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Trend Chart */}
      <div className="card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          Performance Trend
          <Tooltip text="Shows how precision changes over time. Upward trends indicate improving quality. Sudden drops may indicate drift, configuration issues, or data quality problems. Use this to spot when performance degraded and correlate with system changes.">
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </Tooltip>
        </h2>
        {timeseriesLoading ? (
          <div className="h-[300px] flex items-center justify-center text-slate-400">
            Loading trend data...
          </div>
        ) : trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="timestamp" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} domain={[0, 1]} />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorValue)"
                name="Precision"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-slate-400">
            No trend data available for this period
          </div>
        )}
      </div>

      {/* Runs Table */}
      <div className="card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          Evaluation Runs
          <Tooltip text="Complete list of all evaluation runs with key metrics. Click on any run to see detailed breakdown. Use the filters above to narrow down to specific time periods, agents, or search for specific queries.">
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </Tooltip>
        </h2>
        {runsLoading ? (
          <div className="text-center py-12 text-slate-400">Loading runs...</div>
        ) : runs.length === 0 ? (
          <div className="text-center py-12">
            <XCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No evaluation runs found</p>
            <p className="text-sm text-slate-500 mt-1">
              Try adjusting your filters or time range
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left text-slate-400 text-xs font-medium p-3">Timestamp</th>
                  <th className="text-left text-slate-400 text-xs font-medium p-3">Run ID</th>
                  <th className="text-left text-slate-400 text-xs font-medium p-3">Query</th>
                  <th className="text-left text-slate-400 text-xs font-medium p-3">Agent</th>
                  <th className="text-right text-slate-400 text-xs font-medium p-3">Precision</th>
                  <th className="text-right text-slate-400 text-xs font-medium p-3">Faithfulness</th>
                  <th className="text-center text-slate-400 text-xs font-medium p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr
                    key={run.run_id}
                    className="border-b border-slate-800 hover:bg-dark-850 transition-colors cursor-pointer"
                  >
                    <td className="p-3 text-xs text-slate-400">
                      {new Date(run.created_at).toLocaleString()}
                    </td>
                    <td className="p-3 text-xs font-mono text-primary-400">
                      {run.run_id.slice(0, 12)}...
                    </td>
                    <td className="p-3 text-sm text-white max-w-md truncate">
                      {run.query || 'N/A'}
                    </td>
                    <td className="p-3 text-xs text-slate-300">{run.agent_id}</td>
                    <td className="p-3 text-right">
                      <span
                        className={`text-sm font-semibold ${
                          (run.precision || 0) >= 0.8
                            ? 'text-success-500'
                            : (run.precision || 0) >= 0.6
                            ? 'text-warning-500'
                            : 'text-critical-500'
                        }`}
                      >
                        {((run.precision || 0) * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <span
                        className={`text-sm font-semibold ${
                          (run.faithfulness || 0) >= 0.9
                            ? 'text-success-500'
                            : (run.faithfulness || 0) >= 0.7
                            ? 'text-warning-500'
                            : 'text-critical-500'
                        }`}
                      >
                        {((run.faithfulness || 0) * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="p-3 text-center">
                      {(run.precision || 0) >= 0.7 ? (
                        <CheckCircle className="w-4 h-4 text-success-500 inline" />
                      ) : (
                        <XCircle className="w-4 h-4 text-critical-500 inline" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper function to get start time based on range
function getStartTime(range: string): string {
  const now = new Date();
  switch (range) {
    case '24h':
      return new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString();
    case '7d':
      return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();
    case '30d':
      return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString();
    case '90d':
      return new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString();
    default:
      return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();
  }
}
