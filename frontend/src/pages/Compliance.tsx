import { mockCompliance } from '../data/mockData';
import GaugeChart from 'react-gauge-chart';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend, Tooltip } from 'recharts';

export default function Compliance() {
  const frameworks = mockCompliance;
  const aiciFramework = frameworks.find((f) => f.id === 'aici');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Compliance Center
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Regulatory compliance across multiple frameworks
        </p>
      </div>

      {/* Hero Section - AICI Score */}
      <div className="card p-8 text-center">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
          Overall AI Compliance Index (AICI)
        </h2>
        <div className="flex justify-center">
          <div className="w-64">
            <GaugeChart
              id="aici-score"
              nrOfLevels={3}
              colors={['#f43f5e', '#f59e0b', '#10b981']}
              arcWidth={0.3}
              percent={(aiciFramework?.score || 0) / 100}
              textColor={document.documentElement.classList.contains('dark') ? '#f1f5f9' : '#0f172a'}
            />
          </div>
        </div>
        <div className="flex items-center justify-center gap-2 mt-4">
          <div className="w-3 h-3 rounded-full bg-success-500"></div>
          <span className="text-sm text-slate-600 dark:text-slate-400">Compliant</span>
        </div>
      </div>

      {/* Framework Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {frameworks.filter(f => f.id !== 'aici').map((framework) => (
          <div key={framework.id} className="metric-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {framework.acronym}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {framework.name}
                </p>
              </div>
              <span
                className={`badge ${
                  framework.status === 'compliant'
                    ? 'badge-success'
                    : framework.status === 'at_risk'
                    ? 'badge-warning'
                    : 'badge-critical'
                }`}
              >
                {framework.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            <div className="flex justify-center my-4">
              <div className="w-32">
                <GaugeChart
                  id={`gauge-${framework.id}`}
                  nrOfLevels={3}
                  colors={['#f43f5e', '#f59e0b', '#10b981']}
                  arcWidth={0.25}
                  percent={framework.score / 100}
                  textColor={document.documentElement.classList.contains('dark') ? '#f1f5f9' : '#0f172a'}
                  hideText={false}
                />
              </div>
            </div>

            <div className="space-y-2">
              {framework.pillars.map((pillar) => (
                <div key={pillar.name} className="flex items-center justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-400">{pillar.name}</span>
                  <span className="font-medium text-slate-900 dark:text-white">
                    {pillar.score.toFixed(1)}
                  </span>
                </div>
              ))}
            </div>

            <button className="mt-4 text-sm text-primary-600 dark:text-primary-400 hover:underline">
              View Details →
            </button>
          </div>
        ))}
      </div>

      {/* Master Radar Chart */}
      <div className="card p-6">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
          Compliance Framework Comparison
        </h2>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart>
            <PolarGrid stroke="#cbd5e1" />
            <PolarAngleAxis
              dataKey="framework"
              tick={{ fill: '#64748b', fontSize: 12 }}
            />
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#64748b' }} />
            {frameworks.filter(f => f.id !== 'aici').map((framework, idx) => {
              const data = framework.pillars.map((pillar) => ({
                framework: pillar.name,
                score: pillar.score,
              }));
              const colors = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b'];
              return (
                <Radar
                  key={framework.id}
                  name={framework.acronym}
                  data={data}
                  dataKey="score"
                  stroke={colors[idx]}
                  fill={colors[idx]}
                  fillOpacity={0.3}
                />
              );
            })}
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
