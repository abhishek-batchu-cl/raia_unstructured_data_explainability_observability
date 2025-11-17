import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Lightbulb,
  TrendingUp,
  TrendingDown,
  Target,
  Sliders,
  Sparkles,
  ArrowRight,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  X,
  Info,
  Clock,
  DollarSign,
  Zap,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import {
  ScatterChart,
  Scatter,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { api } from '../services/api';
import type {
  CounterfactualScenario,
  SensitivityAnalysis,
  OptimizationRecommendation,
} from '../services/api';

// Tooltip Component
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

// New Scenario Modal
function NewScenarioModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [formData, setFormData] = useState({
    scenario_type: 'chunk_size_optimization',
    parameter: 'chunk_size',
    original_value: '512',
    alternative_value: '1024',
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-dark-900 border border-dark-700 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-700">
          <div>
            <h2 className="text-xl font-bold text-white">Run New What-If Scenario</h2>
            <p className="text-sm text-slate-400 mt-1">
              Test how configuration changes would impact your system
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-dark-800 rounded-lg">
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Form */}
        <div className="p-6 space-y-6">
          {/* Scenario Type */}
          <div>
            <label className="block text-sm font-semibold text-white mb-2">Scenario Type</label>
            <select
              value={formData.scenario_type}
              onChange={(e) => setFormData({ ...formData, scenario_type: e.target.value })}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-4 py-2.5"
            >
              <option value="chunk_size_optimization">Chunk Size Optimization</option>
              <option value="model_parameter_tuning">Model Parameter Tuning</option>
              <option value="retrieval_config">Retrieval Configuration</option>
              <option value="model_upgrade">Model Upgrade</option>
              <option value="hybrid_retrieval">Hybrid Retrieval</option>
            </select>
          </div>

          {/* Parameter */}
          <div>
            <label className="block text-sm font-semibold text-white mb-2">Parameter to Test</label>
            <select
              value={formData.parameter}
              onChange={(e) => setFormData({ ...formData, parameter: e.target.value })}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-4 py-2.5"
            >
              <option value="chunk_size">Chunk Size</option>
              <option value="temperature">Temperature</option>
              <option value="top_k">Top-K Documents</option>
              <option value="max_tokens">Max Tokens</option>
              <option value="embedding_model">Embedding Model</option>
            </select>
          </div>

          {/* Original Value */}
          <div>
            <label className="block text-sm font-semibold text-white mb-2">Original Value</label>
            <input
              type="text"
              value={formData.original_value}
              onChange={(e) => setFormData({ ...formData, original_value: e.target.value })}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-4 py-2.5"
              placeholder="e.g., 512"
            />
          </div>

          {/* Alternative Value */}
          <div>
            <label className="block text-sm font-semibold text-white mb-2">Alternative Value</label>
            <input
              type="text"
              value={formData.alternative_value}
              onChange={(e) => setFormData({ ...formData, alternative_value: e.target.value })}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-4 py-2.5"
              placeholder="e.g., 1024"
            />
          </div>

          {/* Info Box */}
          <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg p-4">
            <div className="flex gap-3">
              <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-primary-300 font-semibold">How This Works</p>
                <p className="text-xs text-slate-400 mt-1">
                  We'll simulate running your RAG system with the alternative configuration and compare quality, latency, and cost metrics against your current setup.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-dark-700">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button className="btn-primary">
            <Sparkles className="w-4 h-4 mr-2 inline" />
            Run Analysis
          </button>
        </div>
      </div>
    </div>
  );
}

export default function WhatIfAnalysis() {
  const [activeTab, setActiveTab] = useState<'counterfactuals' | 'sensitivity' | 'recommendations'>('counterfactuals');
  const [selectedModificationType, setSelectedModificationType] = useState<string>('all');
  const [selectedParameter, setSelectedParameter] = useState<string>('all');
  const [expandedScenario, setExpandedScenario] = useState<number | null>(null);
  const [expandedRecommendation, setExpandedRecommendation] = useState<number | null>(null);
  const [showNewScenarioModal, setShowNewScenarioModal] = useState(false);

  // Fetch what-if data
  const { data: counterfactuals = [] } = useQuery<CounterfactualScenario[]>({
    queryKey: ['counterfactuals'],
    queryFn: () => api.getCounterfactuals({}),
  });

  const { data: sensitivity = [] } = useQuery<SensitivityAnalysis[]>({
    queryKey: ['sensitivity'],
    queryFn: () => api.getSensitivityAnalysis({}),
  });

  const { data: recommendations = [] } = useQuery<OptimizationRecommendation[]>({
    queryKey: ['recommendations'],
    queryFn: () => api.getOptimizationRecommendations({}),
  });

  // Calculate summary metrics
  const avgImprovement =
    counterfactuals.length > 0
      ? counterfactuals.reduce((acc, c) => acc + Math.abs(c.quality_delta || 0), 0) /
        counterfactuals.length
      : 0;

  const highPriorityRecs = recommendations.filter((r) => r.priority === 'high').length;
  const mostSensitiveParam =
    sensitivity.length > 0
      ? sensitivity.reduce((max, s) =>
          (s.expected_improvement > max.expected_improvement ? s : max)
        ).most_sensitive_param
      : 'N/A';

  // Prepare counterfactual comparison data
  const counterfactualData = counterfactuals.slice(0, 15).map((c, idx) => ({
    name: c.scenario_name || `Scenario ${idx + 1}`,
    original: c.original_quality,
    modified: c.alternative_quality,
    difference: c.quality_delta,
    type: c.scenario_type,
  }));

  // Prepare sensitivity scatter data
  const sensitivityData = sensitivity.map((s) => ({
    parameter: s.most_sensitive_param,
    analysisName: s.analysis_name,
    expectedImprovement: s.expected_improvement,
    numSimulations: s.num_simulations,
  }));

  // Group recommendations by optimization goal
  const recsByGoal = recommendations.reduce((acc, rec) => {
    const goal = rec.optimization_goal || 'Other';
    if (!acc[goal]) acc[goal] = [];
    acc[goal].push(rec);
    return acc;
  }, {} as Record<string, OptimizationRecommendation[]>);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-critical-500 bg-critical-500/20 border-critical-500/30';
      case 'medium':
        return 'text-warning-500 bg-warning-500/20 border-warning-500/30';
      case 'low':
        return 'text-primary-500 bg-primary-500/20 border-primary-500/30';
      default:
        return 'text-slate-500 bg-slate-500/20 border-slate-500/30';
    }
  };

  const getImpactIcon = (improvement: number) => {
    if (improvement > 10) return <TrendingUp className="w-5 h-5 text-success-500" />;
    if (improvement < -10) return <TrendingDown className="w-5 h-5 text-critical-500" />;
    return <ArrowRight className="w-5 h-5 text-slate-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            What-If Analysis
            <Tooltip text="Explore alternative configurations and their impact on quality, latency, and cost. Compare counterfactual scenarios to optimize your RAG system.">
              <HelpCircle className="w-5 h-5 text-slate-400" />
            </Tooltip>
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Counterfactuals, sensitivity analysis, and optimization recommendations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary">
            <Sliders className="w-4 h-4 mr-2 inline" />
            Configure Analysis
          </button>
          <button onClick={() => setShowNewScenarioModal(true)} className="btn-primary">
            <Sparkles className="w-4 h-4 mr-2 inline" />
            Run What-If Scenario
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Counterfactual Scenarios */}
        <div className="card p-6 border border-primary-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Scenarios Tested
                </p>
                <Tooltip text="Total number of alternative configurations tested. Each scenario compares your current setup against a modified configuration.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{counterfactuals.length}</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Target className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Counterfactual analyses</span>
          </div>
        </div>

        {/* Avg Improvement */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg Impact
                </p>
                <Tooltip text="Average quality improvement across all scenarios. Positive values indicate better performance with alternative configurations.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">
                  {avgImprovement.toFixed(2)}
                </span>
                <span className="text-slate-500 text-sm">pts</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Average score difference</span>
          </div>
        </div>

        {/* Most Sensitive Parameter */}
        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Most Sensitive
                </p>
                <Tooltip text="The parameter that has the highest impact on quality when changed. Optimizing this parameter will yield the best improvements.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-xl font-bold text-white truncate">{mostSensitiveParam}</span>
              </div>
            </div>
            <div className="p-2 bg-warning-500/20 rounded-lg">
              <Sliders className="w-6 h-6 text-warning-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Parameter with highest sensitivity</span>
          </div>
        </div>

        {/* High Priority Recommendations */}
        <div className="card p-6 border border-critical-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  High Priority
                </p>
                <Tooltip text="Number of high-priority optimization recommendations. These changes should be implemented first for maximum impact.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-critical-500">{highPriorityRecs}</span>
                <span className="text-slate-500 text-sm">/ {recommendations.length}</span>
              </div>
            </div>
            <div className="p-2 bg-critical-500/20 rounded-lg">
              <Lightbulb className="w-6 h-6 text-critical-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Optimization recommendations</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-dark-700">
          <div className="flex items-center gap-1 p-2">
            <button
              onClick={() => setActiveTab('counterfactuals')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                activeTab === 'counterfactuals'
                  ? 'bg-primary-500/20 text-primary-400'
                  : 'text-slate-400 hover:text-white hover:bg-dark-800'
              }`}
            >
              <Target className="w-4 h-4 inline mr-2" />
              Counterfactual Scenarios
              <span className="ml-2 px-2 py-0.5 rounded-full bg-dark-800 text-xs">
                {counterfactuals.length}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('sensitivity')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                activeTab === 'sensitivity'
                  ? 'bg-primary-500/20 text-primary-400'
                  : 'text-slate-400 hover:text-white hover:bg-dark-800'
              }`}
            >
              <Sliders className="w-4 h-4 inline mr-2" />
              Sensitivity Analysis
              <span className="ml-2 px-2 py-0.5 rounded-full bg-dark-800 text-xs">
                {sensitivity.length}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                activeTab === 'recommendations'
                  ? 'bg-primary-500/20 text-primary-400'
                  : 'text-slate-400 hover:text-white hover:bg-dark-800'
              }`}
            >
              <Lightbulb className="w-4 h-4 inline mr-2" />
              Optimization Recommendations
              <span className="ml-2 px-2 py-0.5 rounded-full bg-dark-800 text-xs">
                {recommendations.length}
              </span>
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Counterfactuals Tab */}
          {activeTab === 'counterfactuals' && (
            <div className="space-y-6">
              {/* Chart */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-white">Original vs Alternative Quality</h2>
                    <p className="text-sm text-slate-400 mt-1">
                      Compare quality scores between current and alternative configurations
                    </p>
                  </div>
                  <select
                    value={selectedModificationType}
                    onChange={(e) => setSelectedModificationType(e.target.value)}
                    className="text-sm bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-1.5"
                  >
                    <option value="all">All Types</option>
                    <option value="chunk_size_optimization">Chunk Size</option>
                    <option value="model_parameter_tuning">Model Parameters</option>
                    <option value="retrieval_config">Retrieval Config</option>
                  </select>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={counterfactualData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                      dataKey="name"
                      stroke="#64748b"
                      tick={{ fill: '#64748b', fontSize: 10 }}
                      angle={-15}
                      textAnchor="end"
                      height={80}
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
                    <Bar dataKey="original" name="Original" fill="#64748b" />
                    <Bar dataKey="modified" name="Alternative" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Scenario Cards */}
              <div className="space-y-3">
                {counterfactuals.map((cf, idx) => (
                  <div
                    key={idx}
                    className="border border-dark-700 rounded-lg bg-dark-850 overflow-hidden"
                  >
                    {/* Card Header */}
                    <div className="p-4">
                      <div className="flex items-start gap-4">
                        <div className="mt-1">{getImpactIcon(cf.quality_delta_pct || 0)}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-semibold text-primary-400 px-2 py-0.5 bg-primary-500/20 rounded">
                              {cf.scenario_type}
                            </span>
                            <span
                              className={`text-sm font-bold ${
                                (cf.quality_delta || 0) > 0 ? 'text-success-500' : 'text-critical-500'
                              }`}
                            >
                              {(cf.quality_delta || 0) > 0 ? '+' : ''}
                              {(cf.quality_delta_pct || 0).toFixed(1)}%
                            </span>
                            {cf.is_improvement ? (
                              <CheckCircle className="w-4 h-4 text-success-500" />
                            ) : (
                              <XCircle className="w-4 h-4 text-critical-500" />
                            )}
                          </div>
                          <h3 className="text-base font-bold text-white">{cf.scenario_name}</h3>
                          <p className="text-sm text-slate-400 mt-1">{cf.recommendation}</p>

                          {/* Metrics Grid */}
                          <div className="grid grid-cols-3 gap-4 mt-3">
                            <div>
                              <div className="flex items-center gap-1 mb-1">
                                <Zap className="w-3.5 h-3.5 text-warning-400" />
                                <span className="text-xs text-slate-500">Quality</span>
                              </div>
                              <div className="text-sm">
                                <span className="text-slate-400">{cf.original_quality.toFixed(2)}</span>
                                <span className="text-slate-600 mx-1">→</span>
                                <span className="text-primary-400 font-semibold">
                                  {cf.alternative_quality.toFixed(2)}
                                </span>
                              </div>
                            </div>
                            <div>
                              <div className="flex items-center gap-1 mb-1">
                                <Clock className="w-3.5 h-3.5 text-warning-400" />
                                <span className="text-xs text-slate-500">Latency</span>
                              </div>
                              <div className="text-sm">
                                <span className="text-slate-400">{cf.original_latency_ms.toFixed(0)}ms</span>
                                <span className="text-slate-600 mx-1">→</span>
                                <span className={`font-semibold ${
                                  (cf.latency_delta_pct || 0) > 0 ? 'text-critical-400' : 'text-success-400'
                                }`}>
                                  {cf.alternative_latency_ms.toFixed(0)}ms
                                </span>
                              </div>
                            </div>
                            <div>
                              <div className="flex items-center gap-1 mb-1">
                                <DollarSign className="w-3.5 h-3.5 text-warning-400" />
                                <span className="text-xs text-slate-500">Cost</span>
                              </div>
                              <div className="text-sm">
                                <span className="text-slate-400">${(cf.original_cost_usd * 1000).toFixed(2)}</span>
                                <span className="text-slate-600 mx-1">→</span>
                                <span className={`font-semibold ${
                                  (cf.cost_delta_pct || 0) > 0 ? 'text-critical-400' : 'text-success-400'
                                }`}>
                                  ${(cf.alternative_cost_usd * 1000).toFixed(2)}
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Expand Button */}
                          <button
                            onClick={() => setExpandedScenario(expandedScenario === idx ? null : idx)}
                            className="mt-3 text-xs text-primary-400 hover:text-primary-300 font-medium flex items-center gap-1"
                          >
                            {expandedScenario === idx ? (
                              <>
                                <ChevronUp className="w-4 h-4" />
                                Show Less
                              </>
                            ) : (
                              <>
                                <ChevronDown className="w-4 h-4" />
                                Show Details
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {expandedScenario === idx && (
                      <div className="border-t border-dark-700 p-4 bg-dark-900/50 space-y-4">
                        {/* Configurations */}
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">
                              Original Configuration
                            </h4>
                            <pre className="text-xs text-slate-300 bg-dark-900 p-3 rounded border border-dark-700 overflow-x-auto">
                              {cf.original_config}
                            </pre>
                          </div>
                          <div>
                            <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">
                              Alternative Configuration
                            </h4>
                            <pre className="text-xs text-slate-300 bg-dark-900 p-3 rounded border border-dark-700 overflow-x-auto">
                              {cf.alternative_config}
                            </pre>
                          </div>
                        </div>

                        {/* Pros and Cons */}
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-xs font-semibold text-success-400 uppercase mb-2 flex items-center gap-1">
                              <CheckCircle className="w-3.5 h-3.5" />
                              Pros
                            </h4>
                            <ul className="space-y-1">
                              {JSON.parse(cf.pros).map((pro: string, i: number) => (
                                <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                                  <span className="text-success-500 mt-0.5">•</span>
                                  {pro}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h4 className="text-xs font-semibold text-critical-400 uppercase mb-2 flex items-center gap-1">
                              <XCircle className="w-3.5 h-3.5" />
                              Cons
                            </h4>
                            <ul className="space-y-1">
                              {JSON.parse(cf.cons).map((con: string, i: number) => (
                                <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                                  <span className="text-critical-500 mt-0.5">•</span>
                                  {con}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        {/* Rationale */}
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">
                            Recommendation Rationale
                          </h4>
                          <p className="text-sm text-slate-300">{cf.recommendation_rationale}</p>
                        </div>

                        {/* Confidence */}
                        <div className="flex items-center justify-between pt-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-500">Confidence:</span>
                            <div className="flex items-center gap-1">
                              <div className="w-32 h-2 bg-dark-800 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-primary-500"
                                  style={{ width: `${(cf.confidence || 0) * 100}%` }}
                                />
                              </div>
                              <span className="text-xs font-semibold text-white">
                                {((cf.confidence || 0) * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                          <button className="btn-primary btn-sm">
                            Apply Configuration →
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sensitivity Tab */}
          {activeTab === 'sensitivity' && (
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-white">Parameter Sensitivity</h2>
                    <p className="text-sm text-slate-400 mt-1">
                      Impact of parameter changes on system performance
                    </p>
                  </div>
                  <select
                    value={selectedParameter}
                    onChange={(e) => setSelectedParameter(e.target.value)}
                    className="text-sm bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-1.5"
                  >
                    <option value="all">All Parameters</option>
                    {[...new Set(sensitivity.map((s) => s.most_sensitive_param))].map((param) => (
                      <option key={param} value={param}>
                        {param}
                      </option>
                    ))}
                  </select>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis
                      type="category"
                      dataKey="parameter"
                      name="Parameter"
                      stroke="#64748b"
                      tick={{ fill: '#64748b', fontSize: 11 }}
                    />
                    <YAxis
                      type="number"
                      dataKey="expectedImprovement"
                      name="Expected Improvement"
                      stroke="#64748b"
                      tick={{ fill: '#64748b', fontSize: 11 }}
                    />
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: '#0f172a',
                        border: '1px solid #1e293b',
                        borderRadius: '8px',
                      }}
                      cursor={{ strokeDasharray: '3 3' }}
                    />
                    <Scatter name="Parameters" data={sensitivityData} fill="#3b82f6">
                      {sensitivityData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={(entry.expectedImprovement || 0) > 0.05 ? '#ef4444' : '#3b82f6'}
                        />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>

              {/* Analysis Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sensitivity.map((s, idx) => (
                  <div key={idx} className="border border-dark-700 rounded-lg bg-dark-850 p-4">
                    <h3 className="text-sm font-bold text-white mb-2">{s.analysis_name}</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400">Most Sensitive</span>
                        <span className="text-sm font-semibold text-primary-400">
                          {s.most_sensitive_param}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400">Least Sensitive</span>
                        <span className="text-sm font-semibold text-slate-500">
                          {s.least_sensitive_param}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400">Expected Improvement</span>
                        <span className="text-lg font-bold text-success-500">
                          +{((s.expected_improvement || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400">Simulations Run</span>
                        <span className="text-sm font-semibold text-white">
                          {s.num_simulations}
                        </span>
                      </div>
                      <div className="pt-2 border-t border-dark-700">
                        <span className="text-xs text-slate-500">Optimal Configuration:</span>
                        <pre className="text-xs text-slate-300 mt-1 bg-dark-900 p-2 rounded overflow-x-auto">
                          {s.optimal_config}
                        </pre>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations Tab */}
          {activeTab === 'recommendations' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">Optimization Recommendations</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Actionable recommendations ranked by priority and expected impact
                </p>
              </div>

              <div className="space-y-4">
                {Object.entries(recsByGoal).map(([goal, recs]) => (
                  <div key={goal}>
                    <h3 className="text-sm font-semibold text-slate-300 uppercase mb-3 flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      {goal}
                    </h3>
                    <div className="space-y-3">
                      {recs.map((rec, idx) => (
                        <div
                          key={idx}
                          className={`border rounded-lg overflow-hidden ${getPriorityColor(
                            rec.priority
                          )}`}
                        >
                          {/* Card Header */}
                          <div className="p-4">
                            <div className="flex items-start gap-4">
                              <div className="mt-1">
                                {rec.priority === 'high' ? (
                                  <AlertCircle className="w-5 h-5" />
                                ) : (
                                  <Lightbulb className="w-5 h-5" />
                                )}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-xs font-bold uppercase px-2 py-0.5 rounded">
                                    {rec.priority} PRIORITY
                                  </span>
                                  <span className="text-xs text-slate-400">•</span>
                                  <span className="text-xs font-semibold">
                                    +{rec.quality_improvement_pct.toFixed(1)}% Quality
                                  </span>
                                  <span className="text-xs text-slate-400">•</span>
                                  <span className="text-xs text-slate-400">
                                    {rec.implementation_difficulty}
                                  </span>
                                </div>
                                <h3 className="text-base font-bold text-white">
                                  {rec.recommendation_name}
                                </h3>
                                <p className="text-sm text-slate-400 mt-1">{rec.priority_rationale}</p>

                                {/* Quick Metrics */}
                                <div className="flex items-center gap-4 mt-3 text-xs">
                                  <div className="flex items-center gap-1">
                                    <Clock className="w-3.5 h-3.5" />
                                    <span>{rec.estimated_implementation_time}</span>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <DollarSign className="w-3.5 h-3.5" />
                                    <span className={rec.cost_savings_pct > 0 ? 'text-success-400' : 'text-critical-400'}>
                                      {rec.cost_savings_pct > 0 ? '+' : ''}
                                      {rec.cost_savings_pct.toFixed(0)}% cost
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-1">
                                    <Zap className="w-3.5 h-3.5" />
                                    <span>ROI: {rec.estimated_roi_pct.toFixed(0)}%</span>
                                  </div>
                                </div>

                                <button
                                  onClick={() => setExpandedRecommendation(expandedRecommendation === idx ? null : idx)}
                                  className="mt-3 text-xs font-medium flex items-center gap-1 hover:opacity-80"
                                >
                                  {expandedRecommendation === idx ? (
                                    <>
                                      <ChevronUp className="w-4 h-4" />
                                      Hide Implementation Details
                                    </>
                                  ) : (
                                    <>
                                      <ChevronDown className="w-4 h-4" />
                                      View Implementation Details
                                    </>
                                  )}
                                </button>
                              </div>
                              <div>
                                <button className="btn-primary btn-sm whitespace-nowrap">
                                  Apply →
                                </button>
                              </div>
                            </div>
                          </div>

                          {/* Expanded Details */}
                          {expandedRecommendation === idx && (
                            <div className="border-t p-4 bg-opacity-50 space-y-4">
                              {/* Implementation Steps */}
                              <div>
                                <h4 className="text-xs font-semibold text-slate-300 uppercase mb-2">
                                  Implementation Steps
                                </h4>
                                <ol className="space-y-2">
                                  {JSON.parse(rec.implementation_steps).map((step: string, i: number) => (
                                    <li key={i} className="text-xs text-slate-300 flex gap-2">
                                      <span className="font-semibold">{i + 1}.</span>
                                      <span>{step}</span>
                                    </li>
                                  ))}
                                </ol>
                              </div>

                              {/* Risks and Mitigations */}
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <h4 className="text-xs font-semibold text-critical-400 uppercase mb-2">
                                    Risks ({rec.risk_level})
                                  </h4>
                                  <ul className="space-y-1">
                                    {JSON.parse(rec.risks).map((risk: string, i: number) => (
                                      <li key={i} className="text-xs text-slate-300 flex gap-2">
                                        <span className="text-critical-500">•</span>
                                        {risk}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                                <div>
                                  <h4 className="text-xs font-semibold text-success-400 uppercase mb-2">
                                    Mitigation Strategies
                                  </h4>
                                  <ul className="space-y-1">
                                    {JSON.parse(rec.mitigation_strategies).map((mitigation: string, i: number) => (
                                      <li key={i} className="text-xs text-slate-300 flex gap-2">
                                        <span className="text-success-500">•</span>
                                        {mitigation}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>

                              {/* Recommended Changes */}
                              <div>
                                <h4 className="text-xs font-semibold text-slate-300 uppercase mb-2">
                                  Recommended Changes
                                </h4>
                                <pre className="text-xs text-slate-300 bg-dark-900 p-3 rounded overflow-x-auto">
                                  {rec.recommended_changes}
                                </pre>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* New Scenario Modal */}
      <NewScenarioModal
        isOpen={showNewScenarioModal}
        onClose={() => setShowNewScenarioModal(false)}
      />
    </div>
  );
}
