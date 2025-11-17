import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link2, FileText, Search, ArrowRight, CheckCircle, AlertCircle, HelpCircle, Info } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
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

interface Attribution {
  id?: number;
  run_id: string;
  answer_span: string;
  answer_start_idx: number;
  answer_end_idx: number;
  source_doc_id: string;
  source_span: string;
  source_start_idx: number;
  source_end_idx: number;
  confidence: number;
  similarity_score: number;
  timestamp: string;
}

export default function Attribution() {
  const [selectedRunId, setSelectedRunId] = useState<string>('all');
  const [minConfidence, setMinConfidence] = useState<number>(0);

  // Fetch attribution data from real API
  const { data, isLoading } = useQuery({
    queryKey: ['attributions'],
    queryFn: () => api.getAttributions({ limit: 50 }),
  });

  // Parse attributions data from JSON
  const attributions = useMemo(() => {
    if (!data?.attributions) return [];
    return data.attributions.flatMap((attr) => {
      try {
        const parsed = JSON.parse(attr.attributions);
        return parsed.map((item: any) => ({
          run_id: attr.run_id,
          answer_span: item.answer_span,
          answer_start_idx: item.answer_start_idx,
          answer_end_idx: item.answer_end_idx,
          source_doc_id: item.source_doc_id,
          source_span: item.source_span,
          source_start_idx: item.source_start_idx,
          source_end_idx: item.source_end_idx,
          confidence: item.confidence,
          similarity_score: item.similarity_score,
          timestamp: attr.created_at,
        }));
      } catch {
        return [];
      }
    });
  }, [data]);

  // Filter by confidence
  const filteredAttributions = attributions.filter((a) => a.confidence >= minConfidence / 100);

  // Calculate summary metrics
  const avgConfidence =
    filteredAttributions.length > 0
      ? filteredAttributions.reduce((acc, a) => acc + a.confidence, 0) /
        filteredAttributions.length
      : 0;
  const highConfidence = filteredAttributions.filter((a) => a.confidence >= 0.8).length;
  const uniqueSources = [...new Set(filteredAttributions.map((a) => a.source_doc_id))].length;

  // Prepare confidence distribution data
  const confidenceBuckets = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0];
  const confidenceDistribution = confidenceBuckets.slice(0, -1).map((min, idx) => ({
    range: `${(min * 100).toFixed(0)}-${(confidenceBuckets[idx + 1] * 100).toFixed(0)}%`,
    count: filteredAttributions.filter(
      (a) => a.confidence >= min && a.confidence < confidenceBuckets[idx + 1]
    ).length,
  }));

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-success-500 bg-success-500/20 border-success-500/30';
    if (confidence >= 0.6) return 'text-primary-500 bg-primary-500/20 border-primary-500/30';
    if (confidence >= 0.4) return 'text-warning-500 bg-warning-500/20 border-warning-500/30';
    return 'text-critical-500 bg-critical-500/20 border-critical-500/30';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            Attribution Mapping
            <Tooltip text="Attribution shows exactly which parts of your RAG system's answer came from which source documents. This helps you verify answer accuracy, understand information flow, and debug incorrect responses by tracking the source of each answer component.">
              <HelpCircle className="w-5 h-5 text-slate-400" />
            </Tooltip>
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Track which answer parts came from which source documents
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary">
            <Search className="w-4 h-4 mr-2 inline" />
            Search Attributions
          </button>
          <button className="btn-primary">
            <FileText className="w-4 h-4 mr-2 inline" />
            Generate Report
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
                  Total Attributions
                </p>
                <Tooltip text="Total number of answer-to-source mappings. Each attribution links a specific part of your answer back to the exact source document and text span where that information came from. More attributions mean more granular source tracking.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">
                  {filteredAttributions.length}
                </span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Link2 className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Answer-source mappings</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Avg Confidence
                </p>
                <Tooltip text="Average confidence score across all attributions. Higher confidence (closer to 100%) means the system is more certain that the answer text actually came from the identified source. Confidence is calculated using semantic similarity and text alignment algorithms.">
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
              <CheckCircle className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Attribution confidence</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  High Confidence
                </p>
                <Tooltip text="Number of attributions with 80% or higher confidence. These are highly reliable source links where you can be very confident the answer text came from the identified source document. Use these to verify answer correctness.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{highConfidence}</span>
                <span className="text-slate-500 text-sm">/ {filteredAttributions.length}</span>
              </div>
            </div>
            <div className="p-2 bg-success-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-success-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">&ge; 80% confidence</span>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Unique Sources
                </p>
                <Tooltip text="Number of different source documents referenced in your answers. A higher number indicates your RAG system is pulling information from diverse sources. A lower number might mean your answers rely too heavily on a few documents.">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
                </Tooltip>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-4xl font-bold text-white">{uniqueSources}</span>
              </div>
            </div>
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <FileText className="w-6 h-6 text-primary-500" />
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Source documents</span>
          </div>
        </div>
      </div>

      {/* How Attribution Works - Explanation Card */}
      <div className="card p-6 bg-primary-500/5 border-2 border-primary-500/30">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-primary-300">How Attribution Works</h3>
            <p className="text-xs text-slate-400 mt-1">
              When your RAG system generates an answer, attribution tracking maps each part of the answer back to its source.
              For example, if the answer is "Python was created in 1991 by Guido van Rossum", attribution shows:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-primary-400">•</span>
                <span><strong>"created in 1991"</strong> → Document: python_history.pdf, Position: 245-260</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-400">•</span>
                <span><strong>"by Guido van Rossum"</strong> → Document: python_creators.txt, Position: 78-97</span>
              </li>
            </ul>
            <p className="text-xs text-slate-400 mt-2">
              This granular tracking helps you verify answer accuracy, debug hallucinations, and understand which sources contribute most to your responses.
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <label className="text-xs text-slate-400 block mb-1">Filter by Run ID</label>
            <select
              value={selectedRunId}
              onChange={(e) => setSelectedRunId(e.target.value)}
              className="w-full bg-dark-800 text-white border border-dark-700 rounded-lg px-3 py-2"
            >
              <option value="all">All Runs</option>
              {[...new Set(attributions.map((a) => a.run_id))].map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="text-xs text-slate-400 block mb-1">
              Min Confidence: {minConfidence}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Confidence Distribution */}
      <div className="card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          Confidence Distribution
          <Tooltip text="Shows how your attributions are distributed across confidence levels. Ideally, most attributions should be in the 80-100% range (green bars). Low confidence attributions (red/orange bars) may indicate the answer contains information not clearly present in source documents.">
            <HelpCircle className="w-4 h-4 text-slate-400" />
          </Tooltip>
        </h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={confidenceDistribution}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="range" stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 11 }} />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '8px',
              }}
            />
            <Bar dataKey="count" name="Attributions">
              {confidenceDistribution.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={index >= 3 ? '#10b981' : index >= 2 ? '#3b82f6' : '#f59e0b'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Attribution List */}
      <div className="card p-6">
        <h2 className="text-lg font-bold text-white mb-4">Attribution Mappings</h2>
        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading attributions...</div>
        ) : filteredAttributions.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No attributions found</p>
            <p className="text-sm text-slate-500 mt-1">
              Run some queries to generate attribution mappings
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredAttributions.map((attr, idx) => (
              <div
                key={idx}
                className={`p-5 border rounded-lg ${getConfidenceColor(attr.confidence)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold uppercase">
                      Confidence: {(attr.confidence * 100).toFixed(1)}%
                    </span>
                    <span className="text-xs text-slate-500">•</span>
                    <span className="text-xs text-slate-500">
                      Similarity: {(attr.similarity_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <span className="text-xs text-slate-500">{attr.run_id.slice(0, 16)}...</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Answer Span */}
                  <div className="bg-dark-900/50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-4 h-4 text-primary-400" />
                      <span className="text-xs font-semibold text-primary-400 uppercase">
                        Answer Span
                      </span>
                    </div>
                    <p className="text-sm text-white">{attr.answer_span}</p>
                    <p className="text-xs text-slate-500 mt-2">
                      Position: {attr.answer_start_idx} - {attr.answer_end_idx}
                    </p>
                  </div>

                  {/* Source Span */}
                  <div className="bg-dark-900/50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-4 h-4 text-success-400" />
                      <span className="text-xs font-semibold text-success-400 uppercase">
                        Source Span
                      </span>
                    </div>
                    <p className="text-sm text-white">{attr.source_span}</p>
                    <p className="text-xs text-slate-500 mt-2">
                      Doc: {attr.source_doc_id} • Position: {attr.source_start_idx} -{' '}
                      {attr.source_end_idx}
                    </p>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Link2 className="w-4 h-4 text-slate-500" />
                    <span className="text-xs text-slate-400">Attribution Link</span>
                  </div>
                  <button className="text-xs text-primary-400 hover:text-primary-300 font-medium">
                    View Full Context →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
