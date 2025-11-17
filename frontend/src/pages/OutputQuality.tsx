import { mockEvaluations } from '../data/mockData';
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle2, XCircle, ArrowUpRight, Activity, Target, Zap } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
  Cell, PieChart, Pie
} from 'recharts';
import { useTenant } from '../context/TenantContext';

export default function OutputQuality() {
  const { currentProject } = useTenant();
  const latestEvaluation = mockEvaluations[0];
  const outputQualityCategory = latestEvaluation?.categoryScores.find(
    (c) => c.category === 'output_quality'
  );

  const metrics = outputQualityCategory?.metrics || [];
  const categoryScore = outputQualityCategory?.score || 0;

  // Get key metrics
  const overallQuality = metrics.find((m) => m.id === 'overall-quality')?.score || 0;
  const correctness = metrics.find((m) => m.id === 'correctness')?.score || 0;
  const relevance = metrics.find((m) => m.id === 'relevance')?.score || 0;
  const completeness = metrics.find((m) => m.id === 'completeness')?.score || 0;
  const coherence = metrics.find((m) => m.id === 'coherence')?.score || 0;
  const hallucinationRate = metrics.find((m) => m.id === 'hallucination-rate')?.score || 0;

  // Trend data for the chart (last 30 days)
  const trendData = mockEvaluations.slice(0, 30).reverse().map((evaluation, index) => ({
    day: `Day ${index + 1}`,
    quality: ((evaluation.categoryScores.find((c) => c.category === 'output_quality')?.score || 0) / 100) * 5,
    correctness: evaluation.categoryScores.find((c) => c.category === 'output_quality')?.metrics.find(m => m.id === 'correctness')?.score || 0,
    relevance: evaluation.categoryScores.find((c) => c.category === 'output_quality')?.metrics.find(m => m.id === 'relevance')?.score || 0,
  }));

  // Radar chart data
  const radarData = [
    { metric: 'Correctness', score: (correctness / 5) * 100, target: 90 },
    { metric: 'Relevance', score: (relevance / 5) * 100, target: 85 },
    { metric: 'Completeness', score: (completeness / 5) * 100, target: 88 },
    { metric: 'Coherence', score: (coherence / 5) * 100, target: 92 },
    { metric: 'Consistency', score: ((metrics.find(m => m.name.includes('Consistency'))?.score || 0) / 5) * 100, target: 87 },
  ];

  // Distribution data
  const distributionData = [
    { name: 'Excellent (4.5-5.0)', value: 234, color: '#10b981' },
    { name: 'Good (3.5-4.5)', value: 456, color: '#3b82f6' },
    { name: 'Fair (2.5-3.5)', value: 123, color: '#f59e0b' },
    { name: 'Poor (<2.5)', value: 45, color: '#ef4444' },
  ];

  const getScoreColor = (score: number, max: number = 5) => {
    const percentage = (score / max) * 100;
    if (percentage >= 85) return 'text-success-500';
    if (percentage >= 70) return 'text-primary-500';
    if (percentage >= 50) return 'text-warning-500';
    return 'text-critical-500';
  };

  const getScoreBgColor = (score: number, max: number = 5) => {
    const percentage = (score / max) * 100;
    if (percentage >= 85) return 'bg-success-500/10 border-success-500/20';
    if (percentage >= 70) return 'bg-primary-500/10 border-primary-500/20';
    if (percentage >= 50) return 'bg-warning-500/10 border-warning-500/20';
    return 'bg-critical-500/10 border-critical-500/20';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-primary-500/10 rounded-lg">
              <Target className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Output Quality</h1>
              <p className="text-slate-400 text-sm mt-0.5">
                {currentProject?.name || 'All Projects'} • Measuring AI response accuracy and relevance
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select className="px-4 py-2 bg-dark-850 border border-dark-700 rounded-lg text-sm text-white focus:outline-none focus:border-primary-600">
            <option>Last 30 days</option>
            <option>Last 7 days</option>
            <option>Last 90 days</option>
          </select>
          <button className="btn-primary">
            <Activity className="w-4 h-4 mr-2 inline" />
            Run Evaluation
          </button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Overall Quality Score */}
        <div className={`card p-6 border ${getScoreBgColor(overallQuality)}`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Quality</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className={`text-4xl font-bold ${getScoreColor(overallQuality)}`}>
                  {overallQuality.toFixed(2)}
                </span>
                <span className="text-slate-500 text-sm">/5.0</span>
              </div>
            </div>
            <CheckCircle2 className="w-8 h-8 text-success-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">+2.3%</span>
            <span className="text-slate-500">vs last week</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Performance</span>
              <span>{((overallQuality / 5) * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-dark-800 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-primary-600 to-success-500 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${(overallQuality / 5) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Correctness */}
        <div className={`card p-6 border ${getScoreBgColor(correctness)}`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Correctness</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className={`text-4xl font-bold ${getScoreColor(correctness)}`}>
                  {correctness.toFixed(2)}
                </span>
                <span className="text-slate-500 text-sm">/5.0</span>
              </div>
            </div>
            <Target className="w-8 h-8 text-primary-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">+1.8%</span>
            <span className="text-slate-500">vs last week</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Accuracy Rate</span>
              <span>{((correctness / 5) * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-dark-800 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-primary-600 to-primary-400 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${(correctness / 5) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Relevance */}
        <div className={`card p-6 border ${getScoreBgColor(relevance)}`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Relevance</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className={`text-4xl font-bold ${getScoreColor(relevance)}`}>
                  {relevance.toFixed(2)}
                </span>
                <span className="text-slate-500 text-sm">/5.0</span>
              </div>
            </div>
            <Zap className="w-8 h-8 text-warning-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingDown className="w-4 h-4 text-critical-500" />
            <span className="text-critical-500 font-medium">-0.5%</span>
            <span className="text-slate-500">vs last week</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Match Rate</span>
              <span>{((relevance / 5) * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-dark-800 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-warning-600 to-warning-400 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${(relevance / 5) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Hallucination Rate */}
        <div className={`card p-6 border ${hallucinationRate < 10 ? 'bg-success-500/10 border-success-500/20' : 'bg-critical-500/10 border-critical-500/20'}`}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Hallucination Rate</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className={`text-4xl font-bold ${hallucinationRate < 10 ? 'text-success-500' : 'text-critical-500'}`}>
                  {hallucinationRate.toFixed(1)}%
                </span>
              </div>
            </div>
            <AlertCircle className={`w-8 h-8 ${hallucinationRate < 10 ? 'text-success-500' : 'text-critical-500'} opacity-50`} />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingDown className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">-1.2%</span>
            <span className="text-slate-500">vs last week</span>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Lower is better</span>
              <span>{(100 - hallucinationRate).toFixed(0)}% accurate</span>
            </div>
            <div className="w-full bg-dark-800 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-success-600 to-success-400 h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${100 - hallucinationRate}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="lg:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-white">Quality Metrics Trend</h2>
              <p className="text-sm text-slate-400 mt-1">30-day rolling average</p>
            </div>
            <div className="flex gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary-500" />
                <span className="text-slate-400">Quality</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-success-500" />
                <span className="text-slate-400">Correctness</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-warning-500" />
                <span className="text-slate-400">Relevance</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="colorQuality" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorCorrectness" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorRelevance" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="day"
                stroke="#64748b"
                tick={{ fill: '#64748b', fontSize: 11 }}
                tickLine={{ stroke: '#334155' }}
              />
              <YAxis
                stroke="#64748b"
                domain={[0, 5]}
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
              <Area
                type="monotone"
                dataKey="quality"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorQuality)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="correctness"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorCorrectness)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="relevance"
                stroke="#f59e0b"
                fillOpacity={1}
                fill="url(#colorRelevance)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Distribution Pie Chart */}
        <div className="card p-6">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-white">Score Distribution</h2>
            <p className="text-sm text-slate-400 mt-1">Last 858 evaluations</p>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={distributionData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {distributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {distributionData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-400">{item.name}</span>
                </div>
                <span className="text-white font-medium">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Radar Chart and Metrics Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Multi-Dimensional Analysis</h2>
          <ResponsiveContainer width="100%" height={350}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis
                dataKey="metric"
                tick={{ fill: '#94a3b8', fontSize: 12 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#64748b', fontSize: 10 }}
                stroke="#334155"
              />
              <Radar
                name="Current Score"
                dataKey="score"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.5}
                strokeWidth={2}
              />
              <Radar
                name="Target"
                dataKey="target"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.2}
                strokeWidth={2}
                strokeDasharray="5 5"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                }}
              />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Detailed Metrics List */}
        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Detailed Metrics</h2>
          <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2">
            {metrics.slice(0, 8).map((metric) => {
              const score = metric.scoringMethod === '1-5' ? metric.score : (metric.score / 100) * 5;
              const percentage = (score / 5) * 100;

              return (
                <div key={metric.id} className="pb-4 border-b border-dark-800 last:border-0">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-white">{metric.name}</h3>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{metric.definition}</p>
                    </div>
                    <div className="text-right ml-4">
                      <span className={`text-lg font-bold ${getScoreColor(score)}`}>
                        {metric.score.toFixed(2)}
                      </span>
                      <span className="text-xs text-slate-500 ml-1">/{metric.scoringMethod === '1-5' ? '5' : '100'}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="w-full bg-dark-800 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full transition-all duration-500 ${
                            percentage >= 85 ? 'bg-success-500' :
                            percentage >= 70 ? 'bg-primary-500' :
                            percentage >= 50 ? 'bg-warning-500' : 'bg-critical-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-xs font-medium text-slate-400 min-w-[45px] text-right">
                      {percentage.toFixed(0)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
