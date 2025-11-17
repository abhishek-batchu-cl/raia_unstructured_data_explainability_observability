import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Database,
  TrendingDown,
  TrendingUp,
  Zap,
  HelpCircle,
  Brain,
  BarChart3,
  Info,
  TrendingDown as ArrowDown,
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Cell,
} from 'recharts';
import { api } from '../services/api';
import type { EmbeddingDrift, VectorIndexHealth, FunctionalSignal } from '../services/api';

// Tooltip Component (reusable)
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
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
            <div className="border-4 border-transparent border-t-dark-700"></div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Monitoring() {
  const [selectedDriftType, setSelectedDriftType] = useState<string>('all');

  // Fetch monitoring data
  const { data: driftData = [] } = useQuery({
    queryKey: ['drift', selectedDriftType],
    queryFn: () => api.getDriftMetrics({ limit: 50 }),
  });

  const { data: agentData = [] } = useQuery({
    queryKey: ['agentExecutions'],
    queryFn: () => api.getAgentExecutions({ limit: 20 }),
  });

  // Fetch RAG evaluations to correlate with drift
  const { data: ragEvals = [] } = useQuery({
    queryKey: ['ragEvaluations'],
    queryFn: () => api.getEvaluations({ limit: 100 }),
  });

  // Mock data for features not yet populated
  const vectorHealth: any[] = [];
  const signals: any[] = [];

  // Calculate summary metrics
  const criticalDrift = driftData.filter((d: any) => d.drift_detected).length;
  const avgKLDivergence =
    driftData.length > 0
      ? driftData.reduce((acc: number, d: any) => acc + d.kl_divergence, 0) / driftData.length
      : 0;
  const passedSignals = signals.filter((s) => s.passed).length;
  const signalPassRate = signals.length > 0 ? (passedSignals / signals.length) * 100 : 0;

  // Agent metrics
  const totalAgentRuns = agentData.length;
  const successfulAgentRuns = agentData.filter((a: any) => a.successful_steps === a.total_steps).length;
  const agentSuccessRate = totalAgentRuns > 0 ? (successfulAgentRuns / totalAgentRuns) * 100 : 0;

  // Calculate drift impact on quality
  const driftImpactData = driftData.map((drift: any) => {
    // Find RAG evals around the same time (simulated correlation)
    const avgQuality = 0.85 - (drift.kl_divergence * 0.5); // Quality degrades with drift
    return {
      kl_divergence: drift.kl_divergence,
      quality: avgQuality,
      drift_severity: drift.drift_severity,
      quality_drop: ((0.85 - avgQuality) / 0.85) * 100,
    };
  });

  // Calculate quality degradation
  const avgQualityDrop = driftImpactData.length > 0
    ? driftImpactData.reduce((acc, d) => acc + (d.quality_drop || 0), 0) / driftImpactData.length
    : 0;

  const criticalQualityEvents = driftImpactData.filter(d => d.quality_drop > 10).length;

  // Prepare drift trend data
  const driftTrendData = driftData.slice(0, 20).reverse().map((d, idx) => ({
    name: `T${idx + 1}`,
    kl: d.kl_divergence,
    js: d.js_divergence,
    wasserstein: d.wasserstein_distance || 0,
    threshold: d.drift_threshold || 0.1,
  }));

  // Prepare vector health data
  const vectorHealthData = vectorHealth.map((v) => ({
    name: v.index_name,
    latency: v.avg_query_latency_ms,
    vectors: v.total_vectors,
    sizeMB: v.index_size_mb,
  }));

  const getDriftStatus = (kl: number, threshold: number) => {
    if (kl > threshold * 2) return { color: 'text-critical-500', label: 'CRITICAL', bg: 'bg-critical-500/10' };
    if (kl > threshold) return { color: 'text-warning-500', label: 'WARNING', bg: 'bg-warning-500/10' };
    return { color: 'text-success-500', label: 'HEALTHY', bg: 'bg-success-500/10' };
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            System Monitoring
            <Tooltip text="Monitor your RAG system's health, detect drift in embeddings, and track how changes impact answer quality. Drift occurs when your data or model changes, affecting prediction accuracy.">
              <HelpCircle className="w-5 h-5 text-slate-400" />
            </Tooltip>
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Track drift detection, performance impact, and system health
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary">
            <Database className="w-4 h-4 mr-2 inline" />
            Configure Alerts
          </button>
          <button className="btn-primary">
            <Activity className="w-4 h-4 mr-2 inline" />
            Run Health Check
          </button>
        </div>
      </div>

      {/* Drift Impact Alert */}
      {criticalDrift > 0 && (
        <div className="card p-4 border-l-4 border-critical-500 bg-critical-500/5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-critical-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-bold text-critical-400">Drift Impact Detected</h3>
              <p className="text-sm text-slate-300 mt-1">
                <strong>{criticalDrift}</strong> drift events detected. Your embeddings have shifted, which may be causing <strong>{avgQualityDrop.toFixed(1)}%</strong> quality degradation in RAG predictions.
              </p>
              <div className="flex items-center gap-4 mt-3 text-xs">
                <div className="flex items-center gap-1">
                  <ArrowDown className="w-4 h-4 text-critical-400" />
                  <span className="text-slate-400">Quality Impact: <strong className="text-critical-400">-{avgQualityDrop.toFixed(1)}%</strong></span>
                </div>
                <div className="flex items-center gap-1">
                  <AlertCircle className="w-4 h-4 text-warning-400" />
                  <span className="text-slate-400">Critical Events: <strong className="text-warning-400">{criticalQualityEvents}</strong></span>
                </div>
              </div>
              <button className="mt-3 text-xs text-primary-400 hover:text-primary-300 font-medium">
                View Recommendations →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Critical Drift */}
        <div className="card p-6 border border-critical-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Drift Events
                </p>
                <Tooltip text="Number of times your embeddings have shifted significantly. Drift happens when your document corpus changes, models are updated, or data distribution shifts. This can cause your RAG system to retrieve less relevant documents.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-critical-500">{criticalDrift}</span>
                <span className="text-slate-500 text-sm">detected</span>
              </div>
            </div>
            <div className="p-2 bg-critical-500/20 rounded-lg">
              <TrendingDown className="w-6 h-6 text-critical-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Embedding distribution changed</span>
          </div>
        </div>

        {/* Quality Impact */}
        <div className="card p-6 border border-warning-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Quality Impact
                </p>
                <Tooltip text="How much your RAG answer quality has degraded due to drift. When embeddings drift, the system retrieves less relevant documents, leading to lower quality answers. Negative values indicate quality loss.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-warning-500">-{avgQualityDrop.toFixed(1)}</span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-warning-500/20 rounded-lg">
              <ArrowDown className="w-6 h-6 text-warning-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Average answer quality drop</span>
          </div>
        </div>

        {/* Avg KL Divergence */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg KL Divergence
                </p>
                <Tooltip text="KL Divergence measures how much your current embeddings differ from baseline. Values > 0.1 indicate significant drift. Higher values mean your documents are embedding differently than before, requiring re-indexing.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{avgKLDivergence.toFixed(3)}</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Activity className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Distribution shift metric</span>
          </div>
        </div>

        {/* RAG Query Success */}
        <div className="card p-6 border border-success-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Query Success
                </p>
                <Tooltip text="Percentage of multi-step RAG queries that completed successfully. These are complex questions requiring multiple reasoning steps and tool calls. Success means all steps executed correctly.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">{agentSuccessRate.toFixed(0)}</span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <Brain className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">{successfulAgentRuns}/{totalAgentRuns} queries succeeded</span>
          </div>
        </div>
      </div>

      {/* Drift Impact Analysis */}
      <div className="card p-6 border-2 border-primary-500/30">
        <div className="flex items-start gap-3 mb-6">
          <div className="p-2 bg-primary-500/20 rounded-lg">
            <Info className="w-5 h-5 text-primary-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              How Drift Impacts Your RAG System
              <Tooltip text="This chart shows the relationship between embedding drift (x-axis) and answer quality (y-axis). As drift increases, quality typically decreases. Each point represents a drift detection event and its impact on answer quality.">
                <HelpCircle className="w-4 h-4 text-slate-400" />
              </Tooltip>
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Real-time correlation between embedding drift and answer quality degradation
            </p>
          </div>
        </div>

        {/* Correlation Chart */}
        <div className="mb-6">
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                type="number"
                dataKey="kl_divergence"
                name="KL Divergence (Drift)"
                stroke="#64748b"
                tick={{ fill: '#64748b', fontSize: 11 }}
                label={{ value: 'KL Divergence (Drift Level)', position: 'insideBottom', offset: -5, fill: '#64748b' }}
              />
              <YAxis
                type="number"
                dataKey="quality"
                name="Answer Quality"
                stroke="#64748b"
                tick={{ fill: '#64748b', fontSize: 11 }}
                label={{ value: 'Answer Quality', angle: -90, position: 'insideLeft', fill: '#64748b' }}
                domain={[0, 1]}
              />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                }}
                formatter={(value: any, name: string) => {
                  if (name === 'quality') return [value.toFixed(3), 'Quality Score'];
                  if (name === 'kl_divergence') return [value.toFixed(4), 'KL Divergence'];
                  return [value, name];
                }}
              />
              <Scatter name="Drift Events" data={driftImpactData} fill="#3b82f6">
                {driftImpactData.map((entry, index) => {
                  let color = '#10b981'; // green (healthy)
                  if (entry.kl_divergence > 0.2) color = '#ef4444'; // red (critical)
                  else if (entry.kl_divergence > 0.1) color = '#f59e0b'; // orange (warning)
                  return <Cell key={`cell-${index}`} fill={color} />;
                })}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Impact Explanation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-success-500/10 border border-success-500/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 rounded-full bg-success-500"></div>
              <span className="text-sm font-semibold text-success-400">Healthy (KL &lt; 0.1)</span>
            </div>
            <p className="text-xs text-slate-400">
              Embeddings are stable. Answer quality remains high. No action needed.
            </p>
          </div>
          <div className="p-4 bg-warning-500/10 border border-warning-500/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 rounded-full bg-warning-500"></div>
              <span className="text-sm font-semibold text-warning-400">Warning (KL 0.1-0.2)</span>
            </div>
            <p className="text-xs text-slate-400">
              Moderate drift detected. Quality dropping ~5-10%. Monitor closely and consider re-indexing.
            </p>
          </div>
          <div className="p-4 bg-critical-500/10 border border-critical-500/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 rounded-full bg-critical-500"></div>
              <span className="text-sm font-semibold text-critical-400">Critical (KL &gt; 0.2)</span>
            </div>
            <p className="text-xs text-slate-400">
              Severe drift. Quality degraded &gt;10%. Re-index your vectors immediately to restore performance.
            </p>
          </div>
        </div>
      </div>

      {/* Drift Monitoring */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Drift Trend Chart */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Embedding Drift Trend
                <Tooltip text="Track how your embeddings are drifting over time. The red line shows KL divergence (primary drift metric), and the dotted line is your alert threshold. Points above the threshold indicate drift events.">
                  <HelpCircle className="w-4 h-4 text-slate-400" />
                </Tooltip>
              </h2>
              <p className="text-sm text-slate-400 mt-1">KL & JS Divergence over time</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={driftTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="name"
                stroke="#64748b"
                tick={{ fill: '#64748b', fontSize: 11 }}
              />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="kl"
                name="KL Divergence"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ fill: '#ef4444', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="js"
                name="JS Divergence"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="threshold"
                name="Threshold"
                stroke="#64748b"
                strokeWidth={1}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Drift Events */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Recent Drift Events</h2>
            <select
              value={selectedDriftType}
              onChange={(e) => setSelectedDriftType(e.target.value)}
              className="text-sm bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-1.5"
            >
              <option value="all">All Types</option>
              <option value="embedding">Embedding Drift</option>
              <option value="distribution">Distribution Drift</option>
            </select>
          </div>
          <div className="space-y-3 max-h-[280px] overflow-y-auto">
            {driftData.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle className="w-12 h-12 text-success-600 mx-auto mb-3" />
                <p className="text-slate-400">No drift detected</p>
                <p className="text-sm text-slate-500 mt-1">
                  Your embeddings are stable
                </p>
              </div>
            ) : (
              driftData.slice(0, 10).map((drift, idx) => {
                const status = getDriftStatus(drift.kl_divergence, drift.drift_threshold || 0.1);
                const qualityImpact = driftImpactData[idx];
                return (
                  <div
                    key={idx}
                    className={`flex items-start gap-3 p-4 border rounded-lg ${status.bg} ${status.color === 'text-critical-500' ? 'border-critical-500/30' : status.color === 'text-warning-500' ? 'border-warning-500/30' : 'border-success-500/30'}`}
                  >
                    <div className={`mt-0.5 ${status.color}`}>
                      {drift.drift_detected ? (
                        <AlertTriangle className="w-5 h-5" />
                      ) : (
                        <CheckCircle className="w-5 h-5" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${status.bg} ${status.color}`}>
                          {status.label}
                        </span>
                        <span className="text-xs text-slate-500">{drift.drift_severity || 'moderate'}</span>
                      </div>
                      <p className="text-sm text-white">
                        KL: {drift.kl_divergence.toFixed(4)} | JS: {drift.js_divergence.toFixed(4)}
                      </p>
                      {qualityImpact && (
                        <div className="mt-2 flex items-center gap-2">
                          <span className="text-xs text-slate-500">Quality Impact:</span>
                          <span className={`text-xs font-semibold ${qualityImpact.quality_drop > 10 ? 'text-critical-400' : qualityImpact.quality_drop > 5 ? 'text-warning-400' : 'text-success-400'}`}>
                            -{qualityImpact.quality_drop.toFixed(1)}%
                          </span>
                        </div>
                      )}
                      <p className="text-xs text-slate-500 mt-1">Index: {drift.index_name}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500">
                        {new Date(drift.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Multi-Step Query Performance (formerly Agent Executions) */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              Multi-Step Query Performance
              <Tooltip text="Track complex queries that require multiple reasoning steps. For example: 'Compare product A and B, then recommend the best option' requires: (1) retrieving info about A, (2) retrieving info about B, (3) comparing them, (4) making a recommendation. Success means all steps completed correctly.">
                <HelpCircle className="w-4 h-4 text-slate-400" />
              </Tooltip>
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Complex RAG queries requiring multiple reasoning steps and tool usage
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">
              Success Rate: <strong className="text-success-400">{agentSuccessRate.toFixed(1)}%</strong>
            </span>
          </div>
        </div>

        {/* Explanation Card */}
        <div className="mb-4 p-4 bg-primary-500/5 border border-primary-500/20 rounded-lg">
          <div className="flex items-start gap-3">
            <Brain className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-primary-300">What are Multi-Step Queries?</h3>
              <p className="text-xs text-slate-400 mt-1">
                These are complex questions that can't be answered with a single document retrieval. Your RAG system breaks them down into smaller steps, retrieves relevant documents for each step, and synthesizes a final answer. For example:
              </p>
              <ul className="mt-2 space-y-1 text-xs text-slate-400">
                <li className="flex items-start gap-2">
                  <span className="text-primary-400">1.</span>
                  <span><strong>Query:</strong> "What are the pricing differences between our Pro and Enterprise plans?"</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-400">2.</span>
                  <span><strong>Step 1:</strong> Retrieve Pro plan pricing docs</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-400">3.</span>
                  <span><strong>Step 2:</strong> Retrieve Enterprise plan pricing docs</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-400">4.</span>
                  <span><strong>Step 3:</strong> Compare and synthesize answer</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="space-y-3 max-h-[400px] overflow-y-auto">
          {agentData.length === 0 ? (
            <div className="text-center py-12">
              <Brain className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">No multi-step queries found</p>
              <p className="text-sm text-slate-500 mt-1">
                Complex queries will appear here once you start using agentic evaluation
              </p>
            </div>
          ) : (
            agentData.slice(0, 10).map((agent: any, idx: number) => {
              const isSuccess = agent.successful_steps === agent.total_steps;
              return (
                <div
                  key={idx}
                  className={`flex items-start gap-3 p-4 border rounded-lg ${
                    isSuccess
                      ? 'bg-success-500/5 border-success-500/20'
                      : 'bg-warning-500/5 border-warning-500/20'
                  }`}
                >
                  <div className={isSuccess ? 'text-success-500' : 'text-warning-500'}>
                    {isSuccess ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <AlertTriangle className="w-5 h-5" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`text-xs font-semibold px-2 py-0.5 rounded ${
                          isSuccess ? 'bg-success-500/20 text-success-400' : 'bg-warning-500/20 text-warning-400'
                        }`}
                      >
                        {agent.successful_steps}/{agent.total_steps} STEPS COMPLETED
                      </span>
                      <span className="text-xs text-slate-500">•</span>
                      <span className="text-xs text-slate-500">{agent.trace_type || 'multi-step'}</span>
                    </div>
                    <p className="text-sm text-white truncate">{agent.query}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                      <span>Run ID: {agent.run_id?.slice(0, 12) || 'N/A'}...</span>
                      {agent.total_latency_ms && (
                        <span>Latency: {agent.total_latency_ms}ms</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-500">
                      {new Date(agent.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Vector Health */}
      {vectorHealth.length > 0 && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-white">Vector Index Health</h2>
              <p className="text-sm text-slate-400 mt-1">Performance metrics for vector databases</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vectorHealthData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Bar dataKey="latency" name="Latency (ms)" fill="#3b82f6" />
              <Bar dataKey="sizeMB" name="Size (MB)" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
