/**
 * RAIA Enterprise API Service
 * ============================
 * Complete API client for all RAIA backend endpoints
 *
 * Endpoints:
 * - Dashboard & Summary
 * - RAG Metrics (retrieval, answer quality, semantic, attribution)
 * - Agent Metrics (executions, decisions, node metrics)
 * - Pipeline Metrics
 * - Monitoring (drift, vector health, signals)
 * - What-If Analysis (counterfactuals, sensitivity, optimization)
 * - Analytics (timeseries, export)
 * - Run Details
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ============================================================================
// Response Types
// ============================================================================

export interface DashboardSummary {
  total_runs: number;
  avg_faithfulness: number;
  avg_hallucination: number;
  avg_precision: number;
  avg_recall: number;
  avg_latency_ms: number;
  total_attributions: number;
  total_reasoning_traces: number;
  drift_detected: boolean;
}

export interface RetrievalMetric {
  id?: number;
  run_id: string;
  query: string;
  precision_at_k: number;
  recall_at_k: number;
  f1_at_k?: number;
  mrr?: number;
  ndcg_at_k?: number;
  retrieved_count: number;
  relevant_count: number;
  timestamp: string;
}

export interface AnswerQualityMetric {
  id?: number;
  run_id: string;
  query: string;
  answer: string;
  faithfulness: number;
  hallucination_score: number;
  relevance_score: number;
  correctness_score?: number;
  completeness_score?: number;
  timestamp: string;
}

export interface SemanticScore {
  id?: number;
  run_id: string;
  query: string;
  answer: string;
  semantic_similarity: number;
  coherence_score: number;
  fluency_score: number;
  timestamp: string;
}

export interface NodeMetrics {
  id?: number;
  run_id: string;
  node_name: string;
  node_type: string;
  execution_time_ms: number;
  input_tokens?: number;
  output_tokens?: number;
  success: boolean;
  error_message?: string;
  timestamp: string;
}

export interface PipelineMetrics {
  id?: number;
  run_id: string;
  total_execution_time_ms: number;
  total_nodes: number;
  successful_nodes: number;
  failed_nodes: number;
  total_input_tokens: number;
  total_output_tokens: number;
  timestamp: string;
}

export interface AgentExecution {
  id?: number;
  run_id: string;
  agent_name: string;
  task: string;
  status: 'success' | 'error' | 'in_progress';
  steps_completed: number;
  total_steps: number;
  tools_used: string[];
  final_output?: string;
  error_message?: string;
  execution_time_ms: number;
  timestamp: string;
}

export interface AgentDecision {
  id?: number;
  run_id: string;
  step_number: number;
  decision_type: string;
  reasoning: string;
  confidence: number;
  alternatives_considered: number;
  timestamp: string;
}

export interface EmbeddingDrift {
  id?: number;
  run_id: string;
  drift_type: string;
  kl_divergence: number;
  js_divergence: number;
  wasserstein_distance?: number;
  avg_similarity_to_baseline: number;
  drift_detected: boolean;
  threshold_used: number;
  timestamp: string;
}

export interface VectorIndexHealth {
  id?: number;
  index_name: string;
  total_vectors: number;
  avg_query_latency_ms: number;
  index_size_mb: number;
  last_updated: string;
  health_status: string;
  timestamp: string;
}

export interface FunctionalSignal {
  id?: number;
  run_id: string;
  signal_type: string;
  expected_output: string;
  actual_output: string;
  passed: boolean;
  error_message?: string;
  timestamp: string;
}

export interface CounterfactualScenario {
  id?: number;
  run_id: string;
  scenario_name: string;
  scenario_type: string;
  original_config: string;
  alternative_config: string;
  original_quality: number;
  original_latency_ms: number;
  original_cost_usd: number;
  original_metadata: string;
  alternative_quality: number;
  alternative_latency_ms: number;
  alternative_cost_usd: number;
  alternative_metadata: string;
  quality_delta: number;
  quality_delta_pct: number;
  latency_delta_ms: number;
  latency_delta_pct: number;
  cost_delta_usd: number;
  cost_delta_pct: number;
  is_improvement: number;
  recommendation: string;
  recommendation_rationale: string;
  confidence: number;
  pros: string;
  cons: string;
  created_at: string;
  metadata: string;
}

export interface SensitivityAnalysis {
  id?: number;
  run_id: string;
  analysis_name: string;
  parameters: string;
  most_sensitive_param: string;
  least_sensitive_param: string;
  optimal_config: string;
  expected_improvement: number;
  num_simulations: number;
  analysis_duration_ms: number;
  created_at: string;
  metadata: string;
}

export interface OptimizationRecommendation {
  id?: number;
  run_id: string;
  recommendation_name: string;
  optimization_goal: string;
  current_quality: number;
  current_latency_ms: number;
  current_cost_usd: number;
  recommended_changes: string;
  expected_quality: number;
  expected_latency_ms: number;
  expected_cost_usd: number;
  quality_improvement_pct: number;
  latency_improvement_pct: number;
  cost_savings_pct: number;
  implementation_difficulty: string;
  implementation_steps: string;
  estimated_implementation_time: string;
  risk_level: string;
  risks: string;
  mitigation_strategies: string;
  priority: string;
  priority_rationale: string;
  estimated_annual_savings_usd: number;
  estimated_roi_pct: number;
  created_at: string;
  metadata: string;
}

export interface TimeseriesDataPoint {
  timestamp: string;
  value: number;
}

export interface RunDetails {
  run_id: string;
  retrieval?: RetrievalMetric;
  answer_quality?: AnswerQualityMetric;
  semantic?: SemanticScore;
  attributions: any[];
  reasoning?: any;
  node_metrics: NodeMetrics[];
  pipeline?: PipelineMetrics;
}

// ============================================================================
// API Client
// ============================================================================

class RAIAApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`API Error: ${response.status} - ${error}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  }

  // ========== DASHBOARD ==========

  async getDashboard(): Promise<DashboardSummary> {
    return this.request<DashboardSummary>('/api/dashboard');
  }

  // ========== METRICS ==========

  async getRetrievalMetrics(params?: {
    limit?: number;
    offset?: number;
    run_id?: string;
  }): Promise<RetrievalMetric[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<RetrievalMetric[]>(
      `/api/retrieval${query ? `?${query}` : ''}`
    );
  }

  async getAnswerQuality(params?: {
    limit?: number;
    offset?: number;
    run_id?: string;
  }): Promise<AnswerQualityMetric[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<AnswerQualityMetric[]>(
      `/api/answer-quality${query ? `?${query}` : ''}`
    );
  }

  async getSemanticScores(params?: {
    limit?: number;
    offset?: number;
    run_id?: string;
  }): Promise<SemanticScore[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<SemanticScore[]>(
      `/api/semantic${query ? `?${query}` : ''}`
    );
  }

  async getNodeMetrics(params?: {
    limit?: number;
    offset?: number;
    run_id?: string;
  }): Promise<NodeMetrics[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<NodeMetrics[]>(
      `/api/node-metrics${query ? `?${query}` : ''}`
    );
  }

  async getPipelineMetrics(params?: {
    limit?: number;
    offset?: number;
  }): Promise<PipelineMetrics[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<PipelineMetrics[]>(
      `/api/pipeline${query ? `?${query}` : ''}`
    );
  }

  // ========== AGENT ==========

  async getAgentExecutions(params?: {
    limit?: number;
    status?: string;
  }): Promise<AgentExecution[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<AgentExecution[]>(
      `/api/agent/executions${query ? `?${query}` : ''}`
    );
  }

  async getAgentDecisions(params?: {
    run_id?: string;
    limit?: number;
  }): Promise<AgentDecision[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<AgentDecision[]>(
      `/api/agent/decisions${query ? `?${query}` : ''}`
    );
  }

  // ========== MONITORING ==========

  async getEmbeddingDrift(params?: {
    run_id?: string;
    drift_detected?: boolean;
  }): Promise<EmbeddingDrift[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<EmbeddingDrift[]>(
      `/api/monitoring/drift${query ? `?${query}` : ''}`
    );
  }

  async getVectorHealth(): Promise<VectorIndexHealth[]> {
    return this.request<VectorIndexHealth[]>('/api/monitoring/vector-health');
  }

  async getFunctionalSignals(params?: {
    run_id?: string;
    passed?: boolean;
  }): Promise<FunctionalSignal[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<FunctionalSignal[]>(
      `/api/monitoring/signals${query ? `?${query}` : ''}`
    );
  }

  // ========== WHAT-IF ANALYSIS ==========

  async getCounterfactuals(params?: {
    run_id?: string;
    modification_type?: string;
  }): Promise<CounterfactualScenario[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<CounterfactualScenario[]>(
      `/api/whatif/counterfactuals${query ? `?${query}` : ''}`
    );
  }

  async getSensitivityAnalysis(params?: {
    run_id?: string;
    parameter_name?: string;
  }): Promise<SensitivityAnalysis[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<SensitivityAnalysis[]>(
      `/api/whatif/sensitivity${query ? `?${query}` : ''}`
    );
  }

  async getOptimizationRecommendations(params?: {
    run_id?: string;
    category?: string;
  }): Promise<OptimizationRecommendation[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<OptimizationRecommendation[]>(
      `/api/whatif/optimization${query ? `?${query}` : ''}`
    );
  }

  // ========== ANALYTICS ==========

  async getTimeseries(params: {
    metric_name: string;
    hours?: number;
  }): Promise<TimeseriesDataPoint[]> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    return this.request<TimeseriesDataPoint[]>(
      `/api/analytics/timeseries?${query}`
    );
  }

  async exportData(params: {
    table: string;
    format: 'csv' | 'json';
    run_id?: string;
  }): Promise<Blob> {
    const query = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    const response = await fetch(
      `${this.baseUrl}/api/analytics/export?${query}`
    );
    return response.blob();
  }

  // ========== RUNS ==========

  async getRunDetails(runId: string): Promise<RunDetails> {
    return this.request<RunDetails>(`/api/runs/${runId}`);
  }

  // ========== HEALTH ==========

  async checkHealth(): Promise<{ status: string; database: string }> {
    return this.request<{ status: string; database: string }>('/health');
  }

  // ========== EVENT INGESTION (NEW) ==========

  async ingestEvent(event: {
    event_id: string;
    event_type: string;
    timestamp: string;
    tenant: string;
    project: string;
    agent_id: string;
    session_id: string;
    run_id: string;
    data: any;
  }): Promise<{ status: string; event_id: string; message?: string }> {
    return this.request('/api/events/ingest', {
      method: 'POST',
      body: JSON.stringify(event),
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('raia_api_key') || 'demo-key'}`,
      },
    });
  }

  async ingestEventBatch(events: any[]): Promise<{
    status: string;
    processed: number;
    failed: number;
    results: any[];
  }> {
    return this.request('/api/events/batch', {
      method: 'POST',
      body: JSON.stringify({ events }),
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('raia_api_key') || 'demo-key'}`,
      },
    });
  }

  async getEventStats(): Promise<{
    total_events: number;
    events_by_type: Record<string, number>;
    top_tenants: Record<string, number>;
    events_per_minute_last_hour: number;
  }> {
    return this.request('/api/events/stats', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('raia_api_key') || 'demo-key'}`,
      },
    });
  }

  async getEventIngestionHealth(): Promise<{
    status: string;
    service: string;
    database: string;
    total_events: number;
  }> {
    return this.request('/api/events/health');
  }

  // ========== METRICS DASHBOARD (NEW) ==========

  async getDashboardMetrics(params?: {
    tenant?: string;
    project?: string;
    time_range?: string;
  }): Promise<{
    total_runs: number;
    avg_precision: number;
    avg_recall: number;
    avg_f1: number;
    avg_faithfulness: number;
    avg_hallucination: number;
    total_sessions: number;
    total_agents: number;
  }> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request(`/api/metrics/dashboard${query ? `?${query}` : ''}`);
  }

  async getRecentRuns(params?: {
    limit?: number;
    offset?: number;
    tenant?: string;
    project?: string;
    agent_id?: string;
  }): Promise<{
    runs: Array<{
      run_id: string;
      query: string;
      response: string;
      timestamp: string;
      precision?: number;
      recall?: number;
      f1_score?: number;
      faithfulness?: number;
      hallucination_score?: number;
      agent_id: string;
      project: string;
    }>;
    total: number;
  }> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request(`/api/runs${query ? `?${query}` : ''}`);
  }

  // ==========================================================================
  // Explainability APIs
  // ==========================================================================

  async getAttributions(params?: {
    run_id?: string;
    limit?: number;
  }): Promise<{
    attributions: Array<{
      id: number;
      run_id: string;
      query: string;
      answer: string;
      attributions: string;
      overall_confidence: number;
      faithfulness_score: number;
      hallucination_score: number;
      primary_source: string;
      created_at: string;
    }>;
    total: number;
  }> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request(`/api/explainability/attribution${query ? `?${query}` : ''}`);
  }

  async getReasoningTraces(params?: {
    run_id?: string;
    trace_type?: string;
    limit?: number;
  }): Promise<{
    reasoning_traces: Array<{
      id: number;
      run_id: string;
      trace_type: string;
      query: string;
      final_answer: string;
      steps: string;
      total_steps: number;
      successful_steps: number;
      failed_steps: number;
      reasoning_quality_score: number;
      total_latency_ms: number;
      bottleneck_step: string;
      created_at: string;
    }>;
    total: number;
  }> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request(`/api/explainability/reasoning${query ? `?${query}` : ''}`);
  }

  // ==========================================================================
  // Monitoring APIs
  // ==========================================================================

  async getDriftMetrics(params?: {
    limit?: number;
  }): Promise<Array<{
    id: number;
    baseline_version: string;
    current_version: string;
    cosine_drift: number;
    kl_divergence: number;
    js_divergence: number;
    drift_detected: boolean;
    drift_severity: string;
    created_at: string;
  }>> {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return this.request(`/api/monitoring/drift${query ? `?${query}` : ''}`);
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const api = new RAIAApiClient();
export default api;
