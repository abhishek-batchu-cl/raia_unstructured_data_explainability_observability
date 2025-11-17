import { Zap, Clock, DollarSign, TrendingUp, Activity, Box, ArrowUpRight } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { mockEvaluations } from '../data/mockData';
import { useTenant } from '../context/TenantContext';

export default function Performance() {
  const { currentProject } = useTenant();
  const latestEvaluation = mockEvaluations[0];
  const performanceCategory = latestEvaluation?.categoryScores.find(
    (c) => c.category === 'performance'
  );

  const metrics = performanceCategory?.metrics || [];

  // Key Performance Metrics
  const avgLatency = 342;
  const p95Latency = 587;
  const p99Latency = 892;
  const throughput = 245;
  const tokenThroughput = 1847;
  const costPerRequest = 0.024;
  const successRate = 98.7;
  const cacheHitRate = 67.3;

  // Latency distribution data
  const latencyDistribution = [
    { range: '0-100ms', count: 4523, color: '#10b981' },
    { range: '100-300ms', count: 7234, color: '#3b82f6' },
    { range: '300-500ms', count: 2145, color: '#f59e0b' },
    { range: '500-1000ms', count: 456, color: '#ef4444' },
    { range: '>1000ms', count: 89, color: '#991b1b' },
  ];

  // Trend data (24 hours)
  const trendData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i}:00`,
    latency: 280 + Math.random() * 120,
    throughput: 200 + Math.random() * 100,
  }));

  // Cost breakdown
  const costBreakdown = [
    { name: 'Model Inference', value: 0.018, percentage: 75, color: '#3b82f6' },
    { name: 'Tool Usage', value: 0.004, percentage: 16.7, color: '#8b5cf6' },
    { name: 'Storage', value: 0.002, percentage: 8.3, color: '#10b981' },
  ];

  // Tool interaction data
  const toolInteractions = [
    { tool: 'Web Search', count: 1247, avgTime: 234 },
    { tool: 'Database Query', count: 3421, avgTime: 89 },
    { tool: 'API Call', count: 892, avgTime: 456 },
    { tool: 'File Access', count: 567, avgTime: 123 },
    { tool: 'Code Execution', count: 234, avgTime: 678 },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-warning-500/10 rounded-lg">
              <Zap className="w-6 h-6 text-warning-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Performance Metrics</h1>
              <p className="text-slate-400 text-sm mt-0.5">
                {currentProject?.name || 'All Projects'} • Latency, throughput, and cost analysis
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select className="px-4 py-2 bg-[#151b2b] border border-[#1e293b] rounded-lg text-sm text-white focus:outline-none focus:border-primary-600">
            <option>Last 24 hours</option>
            <option>Last 7 days</option>
            <option>Last 30 days</option>
          </select>
          <button className="btn-primary">
            <Activity className="w-4 h-4 mr-2 inline" />
            Performance Test
          </button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-6 border bg-warning-500/10 border-warning-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Latency</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-warning-500">{avgLatency}</span>
                <span className="text-slate-500 text-sm">ms</span>
              </div>
            </div>
            <Clock className="w-8 h-8 text-warning-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">-12%</span>
            <span className="text-slate-500">faster</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex justify-between text-xs text-slate-400">
              <span>P95: {p95Latency}ms</span>
              <span>P99: {p99Latency}ms</span>
            </div>
          </div>
        </div>

        <div className="card p-6 border bg-primary-500/10 border-primary-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Throughput</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-primary-500">{throughput}</span>
                <span className="text-slate-500 text-sm">req/s</span>
              </div>
            </div>
            <Activity className="w-8 h-8 text-primary-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">+8.3%</span>
            <span className="text-slate-500">increase</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <span className="text-xs text-slate-400">{tokenThroughput} tokens/s</span>
          </div>
        </div>

        <div className="card p-6 border bg-success-500/10 border-success-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cost/Request</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">${costPerRequest}</span>
              </div>
            </div>
            <DollarSign className="w-8 h-8 text-success-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">-5.2%</span>
            <span className="text-slate-500">saved</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <span className="text-xs text-slate-400">$34.50 today</span>
          </div>
        </div>

        <div className="card p-6 border bg-success-500/10 border-success-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Success Rate</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">{successRate.toFixed(1)}</span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <Box className="w-8 h-8 text-success-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">1,437 requests today</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="w-full bg-dark-800 rounded-full h-1.5">
              <div className="bg-gradient-to-r from-success-600 to-success-400 h-1.5 rounded-full" style={{ width: `${successRate}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-6">
          <h2 className="text-lg font-bold text-white mb-6">24-Hour Performance Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="latencyG" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hour" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} />
              <Area type="monotone" dataKey="latency" stroke="#f59e0b" fillOpacity={1} fill="url(#latencyG)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Latency Distribution</h2>
          <div className="space-y-3">
            {latencyDistribution.map((item) => (
              <div key={item.range}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-slate-400">{item.range}</span>
                  <span className="text-white font-medium">{item.count.toLocaleString()}</span>
                </div>
                <div className="w-full bg-dark-800 rounded-full h-2">
                  <div className="h-2 rounded-full" style={{ width: `${(item.count / 14447) * 100}%`, backgroundColor: item.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cost & Tools */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Cost Breakdown</h2>
          <div className="space-y-4">
            {costBreakdown.map((item) => (
              <div key={item.name} className="pb-4 border-b border-dark-800 last:border-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-white font-medium">{item.name}</span>
                  </div>
                  <span className="text-lg font-bold text-white">${item.value.toFixed(3)}</span>
                </div>
                <div className="w-full bg-dark-800 rounded-full h-1.5">
                  <div className="h-1.5 rounded-full" style={{ width: `${item.percentage}%`, backgroundColor: item.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Tool Interactions</h2>
          <div className="space-y-3">
            {toolInteractions.map((tool) => (
              <div key={tool.tool} className="flex items-center justify-between p-3 bg-dark-850 border border-dark-800 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white">{tool.tool}</span>
                    <span className="text-xs text-slate-400">{tool.count.toLocaleString()} calls</span>
                  </div>
                  <span className="text-xs text-warning-400">Avg: {tool.avgTime}ms</span>
                </div>
                <ArrowUpRight className="w-4 h-4 text-slate-500 ml-3" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
