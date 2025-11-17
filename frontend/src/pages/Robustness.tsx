import { Shield, AlertTriangle, TrendingUp, Repeat } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTenant } from '../context/TenantContext';

export default function Robustness() {
  const { currentProject } = useTenant();

  const errorRateData = Array.from({ length: 7 }, (_, i) => ({
    day: `Day ${i + 1}`,
    rate: 1.2 + Math.random() * 0.8,
  }));

  const consistencyData = [
    { scenario: 'Similar Prompts', score: 94.2 },
    { scenario: 'Edge Cases', score: 87.5 },
    { scenario: 'Adversarial', score: 82.3 },
    { scenario: 'Multi-turn', score: 91.8 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-success-500/10 rounded-lg">
              <Shield className="w-6 h-6 text-success-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Robustness</h1>
              <p className="text-slate-400 text-sm mt-0.5">
                {currentProject?.name || 'All Projects'} • Consistency and error resilience
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-6 border bg-success-500/10 border-success-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Error Rate</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">1.3%</span>
              </div>
            </div>
            <AlertTriangle className="w-8 h-8 text-success-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">-0.4%</span>
            <span className="text-slate-500">improvement</span>
          </div>
        </div>

        <div className="card p-6 border bg-primary-500/10 border-primary-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Consistency</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-primary-500">89.2%</span>
              </div>
            </div>
            <Repeat className="w-8 h-8 text-primary-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Across 1,247 tests</span>
          </div>
        </div>

        <div className="card p-6 border bg-warning-500/10 border-warning-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Adversarial Defense</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-warning-500">82.3%</span>
              </div>
            </div>
            <Shield className="w-8 h-8 text-warning-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">89 attacks blocked</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Error Rate Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={errorRateData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="day" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="rate" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Consistency by Scenario</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={consistencyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="scenario" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} />
              <Bar dataKey="score" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
