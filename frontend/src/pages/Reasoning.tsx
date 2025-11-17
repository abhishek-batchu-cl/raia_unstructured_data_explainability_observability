import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Brain,
  GitBranch,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  ChevronRight,
  HelpCircle,
  Info,
} from 'lucide-react';
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

interface ReasoningStep {
  step_number: number;
  step_name: string;
  step_type: string;
  description: string;
  rationale: string;
  confidence: number;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  start_time: string;
  end_time: string;
  latency_ms: number;
}

interface ReasoningTrace {
  id?: number;
  run_id: string;
  trace_type: string;
  query: string;
  steps: ReasoningStep[];
  final_answer: string;
  total_latency_ms: number;
  timestamp: string;
}

export default function Reasoning() {
  const [selectedTraceType, setSelectedTraceType] = useState<string>('all');
  const [expandedTrace, setExpandedTrace] = useState<number | null>(null);

  // Fetch reasoning traces from real API
  const { data, isLoading } = useQuery({
    queryKey: ['reasoning', selectedTraceType],
    queryFn: () => api.getReasoningTraces({ limit: 50 }),
  });

  // Parse reasoning traces from JSON
  const traces = useMemo(() => {
    if (!data?.reasoning_traces) return [];
    return data.reasoning_traces.map((trace) => {
      try {
        const steps = JSON.parse(trace.steps);
        return {
          id: trace.id,
          run_id: trace.run_id,
          trace_type: trace.trace_type,
          query: trace.query,
          steps: steps,
          final_answer: trace.final_answer,
          total_latency_ms: trace.total_latency_ms,
          timestamp: trace.created_at,
        };
      } catch {
        return null;
      }
    }).filter(Boolean) as ReasoningTrace[];
  }, [data]);

  // Calculate summary metrics
  const totalSteps = traces.reduce((acc, t) => acc + t.steps.length, 0);
  const avgStepsPerTrace = traces.length > 0 ? totalSteps / traces.length : 0;
  const avgConfidence =
    totalSteps > 0
      ? traces.reduce(
          (acc, t) => acc + t.steps.reduce((sum, s) => sum + s.confidence, 0),
          0
        ) / totalSteps
      : 0;
  const avgLatency =
    traces.length > 0
      ? traces.reduce((acc, t) => acc + t.total_latency_ms, 0) / traces.length
      : 0;

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-success-500';
    if (confidence >= 0.6) return 'text-primary-500';
    if (confidence >= 0.4) return 'text-warning-500';
    return 'text-critical-500';
  };

  const getStepTypeIcon = (type: string) => {
    switch (type) {
      case 'understanding':
        return <Brain className="w-4 h-4" />;
      case 'retrieval':
        return <GitBranch className="w-4 h-4" />;
      case 'generation':
        return <TrendingUp className="w-4 h-4" />;
      default:
        return <CheckCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            Reasoning Traces
            <Tooltip text="Reasoning traces show your AI agent's step-by-step thought process. See how your RAG system breaks down complex queries, retrieves information, and synthesizes answers. Each trace captures the full decision-making chain, helping you debug logic, optimize performance, and understand why specific answers were generated.">
              <HelpCircle className="w-5 h-5 text-slate-400" />
            </Tooltip>
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Step-by-step agent execution and decision-making process
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary">
            <Brain className="w-4 h-4 mr-2 inline" />
            Analyze Reasoning
          </button>
          <button className="btn-primary">
            <GitBranch className="w-4 h-4 mr-2 inline" />
            Compare Traces
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-6 border border-primary-500/20">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Total Traces
                </p>
                <Tooltip text="Total number of reasoning executions captured. Each trace represents one complete query-to-answer cycle, showing all the intermediate steps your agent took to arrive at the final answer.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{traces.length}</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <GitBranch className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Reasoning executions</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg Steps
                </p>
                <Tooltip text="Average number of reasoning steps per trace. More steps indicate complex multi-hop reasoning. Typical values: simple queries (2-3 steps), complex queries (4-7 steps). Very high values may indicate inefficient reasoning chains.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{avgStepsPerTrace.toFixed(1)}</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Per trace</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg Confidence
                </p>
                <Tooltip text="Average confidence across all reasoning steps. High confidence (>80%) means your agent is certain about its decisions. Low confidence may indicate ambiguous queries, insufficient context, or retrieval issues that need investigation.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-success-500">
                  {(avgConfidence * 100).toFixed(1)}
                </span>
                <span className="text-slate-500 text-sm">%</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <Brain className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Decision confidence</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg Latency
                </p>
                <Tooltip text="Average time to complete a full reasoning trace from query to answer. This includes all retrieval, reasoning, and generation steps. Optimize slow traces by reducing steps, improving retrieval speed, or using faster models.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{avgLatency.toFixed(0)}</span>
                <span className="text-slate-500 text-sm">ms</span>
              </div>
            </div>
            <div className="p-2 bg-warning-500/20 rounded-lg">
              <Clock className="w-6 h-6 text-warning-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Processing time</span>
          </div>
        </div>
      </div>

      {/* How Reasoning Traces Work - Explanation Card */}
      <div className="card p-6 bg-primary-500/5 border-2 border-primary-500/30">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-primary-300">Understanding Reasoning Traces</h3>
            <p className="text-xs text-slate-400 mt-1">
              Reasoning traces capture your AI agent's complete thought process from query to answer.
              For example, when asked "What were Tesla's Q4 2023 earnings?", a trace might show:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-primary-400">1.</span>
                <span><strong>Understanding:</strong> Parse query → identify company (Tesla), metric (earnings), timeframe (Q4 2023) → Confidence: 95%</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-400">2.</span>
                <span><strong>Retrieval:</strong> Search for "Tesla Q4 2023 financial report" → Found 5 documents → Confidence: 88%</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-400">3.</span>
                <span><strong>Generation:</strong> Extract earnings figure from doc #2 → Synthesize answer → Confidence: 92%</span>
              </li>
            </ul>
            <p className="text-xs text-slate-400 mt-2">
              Each step shows inputs, outputs, confidence, and latency. This transparency helps you debug incorrect answers, optimize slow queries, and understand your agent's decision-making logic.
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <label className="text-xs text-slate-400 block mb-1">Filter by Trace Type</label>
            <select
              value={selectedTraceType}
              onChange={(e) => setSelectedTraceType(e.target.value)}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-2"
            >
              <option value="all">All Types</option>
              <option value="rag_reasoning">RAG Reasoning</option>
              <option value="agent_reasoning">Agent Reasoning</option>
              <option value="chain_of_thought">Chain of Thought</option>
            </select>
          </div>
        </div>
      </div>

      {/* Reasoning Traces */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="card p-12 text-center text-slate-400">Loading reasoning traces...</div>
        ) : traces.length === 0 ? (
          <div className="card p-12 text-center">
            <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No reasoning traces found</p>
            <p className="text-sm text-slate-500 mt-1">
              Run some queries to generate reasoning traces
            </p>
          </div>
        ) : (
          traces.map((trace, idx) => (
            <div key={idx} className="card p-6">
              {/* Trace Header */}
              <div
                className="flex items-start justify-between cursor-pointer"
                onClick={() => setExpandedTrace(expandedTrace === idx ? null : idx)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xs font-semibold text-primary-400 uppercase">
                      {trace.trace_type}
                    </span>
                    <span className="text-xs text-slate-500">•</span>
                    <span className="text-xs text-slate-500">
                      {trace.steps.length} steps • {trace.total_latency_ms}ms
                    </span>
                  </div>
                  <p className="text-sm text-white font-medium">{trace.query}</p>
                  <p className="text-xs text-slate-500 mt-1">{trace.run_id}</p>
                </div>
                <button className="p-2 hover:bg-dark-800 rounded-lg transition-colors">
                  <ChevronRight
                    className={`w-5 h-5 text-slate-400 transition-transform ${
                      expandedTrace === idx ? 'rotate-90' : ''
                    }`}
                  />
                </button>
              </div>

              {/* Expanded Steps */}
              {expandedTrace === idx && (
                <div className="mt-4 pt-4 border-t border-slate-800">
                  <div className="space-y-3">
                    {trace.steps.map((step, stepIdx) => (
                      <div
                        key={stepIdx}
                        className="relative pl-8 pb-4 border-l-2 border-slate-800 last:border-l-0 last:pb-0"
                      >
                        {/* Step Indicator */}
                        <div className="absolute left-[-9px] top-0 p-1.5 bg-dark-900 border-2 border-slate-800 rounded-full">
                          {getStepTypeIcon(step.step_type)}
                        </div>

                        {/* Step Content */}
                        <div className="bg-dark-850 p-4 rounded-lg border border-dark-800">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-semibold text-white">
                                {step.step_number}. {step.step_name}
                              </span>
                              <span className="text-xs text-slate-500">({step.step_type})</span>
                            </div>
                            <div className="flex items-center gap-3 text-xs">
                              <span className={getConfidenceColor(step.confidence)}>
                                {(step.confidence * 100).toFixed(0)}%
                              </span>
                              <span className="text-slate-500">{step.latency_ms.toFixed(0)}ms</span>
                            </div>
                          </div>

                          <p className="text-sm text-slate-300 mb-2">{step.description}</p>
                          <p className="text-xs text-slate-400 italic">{step.rationale}</p>

                          {/* Inputs/Outputs */}
                          <div className="grid grid-cols-2 gap-3 mt-3">
                            <div className="bg-dark-900/50 p-3 rounded">
                              <p className="text-xs font-semibold text-slate-400 mb-1">INPUTS</p>
                              <pre className="text-xs text-slate-300 overflow-x-auto">
                                {JSON.stringify(step.inputs, null, 2)}
                              </pre>
                            </div>
                            <div className="bg-dark-900/50 p-3 rounded">
                              <p className="text-xs font-semibold text-slate-400 mb-1">OUTPUTS</p>
                              <pre className="text-xs text-slate-300 overflow-x-auto">
                                {JSON.stringify(step.outputs, null, 2)}
                              </pre>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Final Answer */}
                  <div className="mt-4 p-4 bg-success-500/10 border border-success-500/30 rounded-lg">
                    <p className="text-xs font-semibold text-success-400 uppercase mb-2">
                      Final Answer
                    </p>
                    <p className="text-sm text-white">{trace.final_answer}</p>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
