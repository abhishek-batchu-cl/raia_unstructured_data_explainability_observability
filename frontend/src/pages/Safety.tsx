import { Shield, AlertTriangle, Scale, Heart, TrendingDown } from 'lucide-react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTenant } from '../context/TenantContext';

export default function Safety() {
  const { currentProject } = useTenant();

  const biasData = [
    { dimension: 'Gender', score: 92.3 },
    { dimension: 'Age', score: 88.7 },
    { dimension: 'Race', score: 91.5 },
    { dimension: 'Religion', score: 94.1 },
  ];

  const harmfulContent = [
    { category: 'Violence', count: 12, color: '#ef4444' },
    { category: 'Hate Speech', count: 5, color: '#f59e0b' },
    { category: 'Sexual', count: 3, color: '#8b5cf6' },
    { category: 'Self-harm', count: 2, color: '#ef4444' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-critical-500/10 rounded-lg">
              <Shield className="w-6 h-6 text-critical-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Safety & Ethics</h1>
              <p className="text-slate-400 text-sm mt-0.5">
                {currentProject?.name || 'All Projects'} • Bias detection and harmful content monitoring
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-6 border bg-success-500/10 border-success-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Fairness Score</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">91.8%</span>
              </div>
            </div>
            <Scale className="w-8 h-8 text-success-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Across 4 dimensions</span>
          </div>
        </div>

        <div className="card p-6 border bg-warning-500/10 border-warning-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Harmful Content Rate</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-warning-500">0.18%</span>
              </div>
            </div>
            <AlertTriangle className="w-8 h-8 text-warning-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingDown className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">-0.05%</span>
          </div>
        </div>

        <div className="card p-6 border bg-primary-500/10 border-primary-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tone Consistency</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-primary-500">94.2%</span>
              </div>
            </div>
            <Heart className="w-8 h-8 text-primary-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Professional tone</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Bias Detection by Dimension</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={biasData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="dimension" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} />
              <Bar dataKey="score" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Harmful Content Categories</h2>
          <div className="space-y-4">
            {harmfulContent.map((item) => (
              <div key={item.category} className="pb-4 border-b border-dark-800 last:border-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-white font-medium">{item.category}</span>
                  </div>
                  <span className="text-lg font-bold text-white">{item.count}</span>
                </div>
                <p className="text-xs text-slate-400">Flagged instances in last 30 days</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
