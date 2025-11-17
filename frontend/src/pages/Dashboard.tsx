import { Activity, TrendingUp, AlertTriangle, Database, Zap, Shield, Users, CheckCircle, ArrowUpRight } from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { mockEvaluations } from '../data/mockData';
import { useTenant } from '../context/TenantContext';
import { useAlerts } from '../context/AlertContext';

export default function Dashboard() {
  const { currentProject } = useTenant();
  const { getActiveAlerts } = useAlerts();
  const latestEvaluation = mockEvaluations[0];
  const overallScore = latestEvaluation?.overallScore || 0;
  const activeAlerts = getActiveAlerts();
  const criticalAlerts = activeAlerts.filter(a => a.severity === 'critical').length;

  // Calculate summary stats
  const totalEvaluations = mockEvaluations.length;
  const last24hEvaluations = 1247;
  const avgResponseTime = 342;

  // Category scores from latest evaluation
  const categoryScores = latestEvaluation?.categoryScores || [];

  // Trend data for the chart (last 7 days)
  const trendData = mockEvaluations.slice(0, 7).reverse().map((evaluation, index) => ({
    name: `Day ${index + 1}`,
    overall: evaluation.overallScore,
    outputQuality: evaluation.categoryScores.find((c) => c.category === 'output_quality')?.score || 0,
    performance: evaluation.categoryScores.find((c) => c.category === 'performance')?.score || 0,
    safety: evaluation.categoryScores.find((c) => c.category === 'safety')?.score || 0,
  }));

  // Radar data for comprehensive view
  const radarData = categoryScores.map(cat => ({
    category: cat.category.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
    score: cat.score,
    target: 85,
  }));

  // Category icons and colors
  const categoryConfig: Record<string, { icon: any; color: string; bgColor: string }> = {
    output_quality: { icon: CheckCircle, color: 'text-primary-500', bgColor: 'bg-primary-500/10' },
    performance: { icon: Zap, color: 'text-warning-500', bgColor: 'bg-warning-500/10' },
    robustness: { icon: Shield, color: 'text-success-500', bgColor: 'bg-success-500/10' },
    safety: { icon: AlertTriangle, color: 'text-critical-500', bgColor: 'bg-critical-500/10' },
    user_experience: { icon: Users, color: 'text-secondary-500', bgColor: 'bg-secondary-500/10' },
    compliance: { icon: CheckCircle, color: 'text-success-500', bgColor: 'bg-success-500/10' },
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-success-500';
    if (score >= 70) return 'text-primary-500';
    if (score >= 50) return 'text-warning-500';
    return 'text-critical-500';
  };

  const getScoreBg = (score: number) => {
    if (score >= 85) return 'from-success-600 to-success-400';
    if (score >= 70) return 'from-primary-600 to-primary-400';
    if (score >= 50) return 'from-warning-600 to-warning-400';
    return 'from-critical-600 to-critical-400';
  };

  const categoryLabels: Record<string, string> = {
    output_quality: 'Output Quality',
    performance: 'Performance',
    robustness: 'Robustness',
    safety: 'Safety & Ethics',
    user_experience: 'User Experience',
    compliance: 'Compliance',
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">AI Health Dashboard</h1>
          <p className="text-slate-400 text-sm mt-0.5">
            {currentProject?.name || 'All Projects'} • Real-time monitoring and analytics
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
        {/* Overall AI Health Score */}
        <div className="card p-6 border border-primary-500/20 bg-gradient-to-br from-primary-500/5 to-transparent">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Health Score</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className={`text-4xl font-bold ${getScoreColor(overallScore)}`}>
                  {overallScore.toFixed(1)}
                </span>
                <span className="text-slate-500 text-sm">/100</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">+5.2%</span>
            <span className="text-slate-500">vs last week</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-800">
            <div className="w-full bg-dark-800 rounded-full h-2">
              <div
                className={`h-2 rounded-full bg-gradient-to-r ${getScoreBg(overallScore)} transition-all duration-500`}
                style={{ width: `${overallScore}%` }}
              />
            </div>
          </div>
        </div>

        {/* Total Evaluations */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Evaluations</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{totalEvaluations.toLocaleString()}</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-success-500 font-medium">+124</span>
            <span className="text-slate-500">in last 24h</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-800">
            <p className="text-xs text-slate-500">{last24hEvaluations} evaluations today</p>
          </div>
        </div>

        {/* Critical Alerts */}
        <div className="card p-6 border border-critical-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Critical Alerts</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-critical-500">{criticalAlerts}</span>
              </div>
            </div>
            <div className="p-2 bg-critical-500/20 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-critical-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Requires immediate attention</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-800">
            <button className="text-xs text-critical-400 hover:text-critical-300 font-medium">
              View all alerts →
            </button>
          </div>
        </div>

        {/* Avg Response Time */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Response Time</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{avgResponseTime}</span>
                <span className="text-slate-500 text-sm">ms</span>
              </div>
            </div>
            <div className="p-2 bg-warning-500/20 rounded-lg">
              <Zap className="w-6 h-6 text-warning-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">-12%</span>
            <span className="text-slate-500">faster</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-800">
            <p className="text-xs text-slate-500">P95: 587ms • P99: 892ms</p>
          </div>
        </div>
      </div>

      {/* Category Performance Grid */}
      <div>
        <h2 className="text-lg font-bold text-white mb-4">Category Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categoryScores.map((category) => {
            const config = categoryConfig[category.category];
            const Icon = config?.icon || Activity;

            return (
              <div key={category.category} className="card p-5 hover:border-primary-500/30 transition-all cursor-pointer group">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 ${config?.bgColor} rounded-lg group-hover:scale-110 transition-transform`}>
                      <Icon className={`w-5 h-5 ${config?.color}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white text-sm">{categoryLabels[category.category]}</h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {category.metrics.length} metrics
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${getScoreColor(category.score)}`}>
                      {category.score.toFixed(1)}
                    </div>
                    <div className="flex items-center gap-1 mt-1 justify-end">
                      {category.trend === 'up' ? (
                        <>
                          <ArrowUpRight className="w-3 h-3 text-success-500" />
                          <span className="text-xs text-success-500 font-medium">{category.percentChange.toFixed(1)}%</span>
                        </>
                      ) : category.trend === 'down' ? (
                        <>
                          <ArrowUpRight className="w-3 h-3 text-critical-500 rotate-90" />
                          <span className="text-xs text-critical-500 font-medium">{Math.abs(category.percentChange).toFixed(1)}%</span>
                        </>
                      ) : (
                        <span className="text-xs text-slate-500">Stable</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Mini progress bar */}
                <div className="w-full bg-dark-800 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full bg-gradient-to-r ${getScoreBg(category.score)} transition-all duration-500`}
                    style={{ width: `${category.score}%` }}
                  />
                </div>

                <div className="mt-3 pt-3 border-t border-slate-800">
                  <button className="text-xs text-primary-400 hover:text-primary-300 font-medium group-hover:translate-x-1 transition-transform inline-block">
                    View details →
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="lg:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-white">7-Day Performance Trend</h2>
              <p className="text-sm text-slate-400 mt-1">Overall health and key metrics</p>
            </div>
            <div className="flex gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary-500" />
                <span className="text-slate-400">Overall</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-success-500" />
                <span className="text-slate-400">Quality</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-warning-500" />
                <span className="text-slate-400">Performance</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <defs>
                <linearGradient id="overall" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="name"
                stroke="#64748b"
                tick={{ fill: '#64748b', fontSize: 11 }}
                tickLine={{ stroke: '#334155' }}
              />
              <YAxis
                stroke="#64748b"
                domain={[0, 100]}
                tick={{ fill: '#64748b', fontSize: 11 }}
                tickLine={{ stroke: '#334155' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
                }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Line
                type="monotone"
                dataKey="overall"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="outputQuality"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="performance"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Radar Chart */}
        <div className="card p-6">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-white">Category Balance</h2>
            <p className="text-sm text-slate-400 mt-1">All 6 dimensions</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis
                dataKey="category"
                tick={{ fill: '#94a3b8', fontSize: 10 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#64748b', fontSize: 9 }}
                stroke="#334155"
              />
              <Radar
                name="Current"
                dataKey="score"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.6}
                strokeWidth={2}
              />
              <Radar
                name="Target"
                dataKey="target"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.1}
                strokeWidth={1}
                strokeDasharray="5 5"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Alerts */}
      {activeAlerts.length > 0 && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Recent Alerts</h2>
            <button className="text-sm text-primary-400 hover:text-primary-300 font-medium">
              View all →
            </button>
          </div>
          <div className="space-y-3">
            {activeAlerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className="flex items-start gap-3 p-4 bg-dark-850 border border-dark-800 rounded-lg hover:border-dark-700 transition-colors"
              >
                <div className={`mt-0.5 ${
                  alert.severity === 'critical' ? 'text-critical-500' :
                  alert.severity === 'warning' ? 'text-warning-500' : 'text-primary-500'
                }`}>
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded ${
                      alert.severity === 'critical' ? 'bg-critical-500/20 text-critical-400' :
                      alert.severity === 'warning' ? 'bg-warning-500/20 text-warning-400' :
                      'bg-primary-500/20 text-primary-400'
                    }`}>
                      {alert.severity}
                    </span>
                    <span className="text-xs text-slate-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-white">{alert.message}</p>
                </div>
                <button className="text-sm text-primary-400 hover:text-primary-300 font-medium whitespace-nowrap">
                  Details →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
