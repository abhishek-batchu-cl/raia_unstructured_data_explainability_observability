import { Users, ThumbsUp, MessageSquare, TrendingUp } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTenant } from '../context/TenantContext';

export default function UserExperience() {
  const { currentProject } = useTenant();

  const nps = 67;
  const csat = 4.3;
  const avgTurns = 3.8;

  const satisfactionDist = [
    { stars: '5 ⭐', count: 1234 },
    { stars: '4 ⭐', count: 876 },
    { stars: '3 ⭐', count: 234 },
    { stars: '2 ⭐', count: 87 },
    { stars: '1 ⭐', count: 45 },
  ];

  const turnData = Array.from({ length: 7 }, (_, i) => ({
    day: `Day ${i + 1}`,
    turns: 3.5 + Math.random() * 0.8,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-secondary-500/10 rounded-lg">
              <Users className="w-6 h-6 text-secondary-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">User Experience</h1>
              <p className="text-slate-400 text-sm mt-0.5">
                {currentProject?.name || 'All Projects'} • User satisfaction and interaction patterns
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-6 border bg-success-500/10 border-success-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Net Promoter Score</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">{nps}</span>
              </div>
            </div>
            <ThumbsUp className="w-8 h-8 text-success-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-success-500" />
            <span className="text-success-500 font-medium">+5 pts</span>
            <span className="text-slate-500">vs last month</span>
          </div>
        </div>

        <div className="card p-6 border bg-primary-500/10 border-primary-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">CSAT Score</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-primary-500">{csat}</span>
                <span className="text-slate-500 text-sm">/5.0</span>
              </div>
            </div>
            <MessageSquare className="w-8 h-8 text-primary-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">2,476 ratings</span>
          </div>
        </div>

        <div className="card p-6 border bg-warning-500/10 border-warning-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Turn Count</p>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-warning-500">{avgTurns}</span>
              </div>
            </div>
            <MessageSquare className="w-8 h-8 text-warning-500 opacity-50" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Per conversation</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Satisfaction Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={satisfactionDist}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="stars" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-bold text-white mb-6">Conversation Turns Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={turnData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="day" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="turns" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
