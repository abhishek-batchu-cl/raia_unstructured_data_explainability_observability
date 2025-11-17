// Core types for RAIA application

export type MetricCategory =
  | 'output_quality'
  | 'performance'
  | 'robustness'
  | 'safety'
  | 'user_experience'
  | 'compliance';

export type ScoringMethod = '1-5' | '0-100' | 'ms' | 'dollar' | 'count';

export type TrendDirection = 'up' | 'down' | 'stable';

export type AlertSeverity = 'critical' | 'warning' | 'info';

export type EvaluationStatus = 'completed' | 'in_progress' | 'failed';

export type ComplianceStatus = 'compliant' | 'at_risk' | 'non_compliant';

export interface Metric {
  id: string;
  name: string;
  category: MetricCategory;
  score: number;
  scoringMethod: ScoringMethod;
  owner: string;
  definition: string;
  calculationMethod: string;
}

export interface CategoryScore {
  category: MetricCategory;
  score: number;
  metrics: Metric[];
  trend: TrendDirection;
  percentChange: number;
}

export interface Alert {
  id: string;
  severity: AlertSeverity;
  message: string;
  metricId: string;
  timestamp: Date;
  dismissed: boolean;
}

export interface Evaluation {
  id: string;
  timestamp: Date;
  agentId: string;
  agentVersion: string;
  overallScore: number;
  categoryScores: CategoryScore[];
  alerts: Alert[];
  status: EvaluationStatus;
}

export interface CompliancePillar {
  name: string;
  score: number;
}

export interface ComplianceFramework {
  id: string;
  name: string;
  acronym: string;
  score: number;
  pillars: CompliancePillar[];
  status: ComplianceStatus;
}

export interface Agent {
  id: string;
  name: string;
  version: string;
  description: string;
  releaseDate: Date;
}

export interface FilterState {
  dateRange?: {
    from: Date;
    to: Date;
  };
  agentVersions: string[];
  categories: MetricCategory[];
  scoreRange?: {
    min: number;
    max: number;
  };
  searchQuery?: string;
}

// Performance metrics specific types
export interface PerformanceMetrics {
  latency: {
    min: number;
    max: number;
    mean: number;
    median: number;
    p50: number;
    p95: number;
    p99: number;
    distribution: { bucket: string; count: number }[];
  };
  throughput: {
    current: number;
    capacity: number;
    history: { timestamp: Date; value: number }[];
  };
  cost: {
    total: number;
    breakdown: {
      modelInference: number;
      toolUsage: number;
      storage: number;
    };
    history: { timestamp: Date; value: number }[];
  };
  successRate: {
    successful: number;
    failed: number;
    percentage: number;
    history: { timestamp: Date; value: number }[];
  };
  toolInteractions: {
    total: number;
    byTool: { tool: string; count: number }[];
    flow: { source: string; target: string; value: number }[];
  };
}

// User experience specific types
export interface UserExperienceMetrics {
  nps: number;
  csat: number;
  satisfactionDistribution: {
    fiveStars: number;
    fourStars: number;
    threeStars: number;
    twoStars: number;
    oneStar: number;
  };
  turnCount: {
    average: number;
    distribution: { turns: number; frequency: number }[];
    byIntent: { intent: string; average: number }[];
  };
  feedback: {
    id: string;
    rating: number;
    comment: string;
    timestamp: Date;
    sentiment: 'positive' | 'neutral' | 'negative';
  }[];
}

// Safety metrics specific types
export interface SafetyMetrics {
  biasDetection: {
    overall: number;
    byDemographic: { dimension: string; score: number }[];
  };
  harmfulContent: {
    rate: number;
    categories: { category: string; count: number }[];
  };
  fairness: {
    overall: number;
    byGroup: { group: string; score: number }[];
  };
  tone: {
    consistency: number;
    sentimentDistribution: { sentiment: string; percentage: number }[];
  };
}

// Robustness metrics specific types
export interface RobustnessMetrics {
  consistency: {
    score: number;
    variance: { scenario: string; values: number[] }[];
  };
  errorRate: {
    overall: number;
    byType: { type: string; count: number }[];
    history: { timestamp: Date; value: number }[];
  };
  adversarialResilience: {
    score: number;
    attackScenarios: {
      name: string;
      successRate: number;
      sample: { input: string; output: string };
    }[];
  };
}

// Chart data types
export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: string | number;
}

export interface TimeSeriesData {
  timestamp: Date;
  value: number;
  label?: string;
}

export interface SankeyNode {
  name: string;
}

export interface SankeyLink {
  source: number;
  target: number;
  value: number;
}

export interface RadarChartData {
  metric: string;
  value: number;
  fullMark: number;
}

// Report types
export type ReportType = 'executive_summary' | 'technical_deep_dive' | 'compliance_audit' | 'custom';

export interface ReportConfig {
  type: ReportType;
  title: string;
  includedSections: string[];
  format: 'pdf' | 'excel' | 'json' | 'csv';
}

export interface ScheduledReport {
  id: string;
  name: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  schedule: {
    dayOfWeek?: number;
    dayOfMonth?: number;
    time: string;
  };
  config: ReportConfig;
  recipients: string[];
  nextRun: Date;
  active: boolean;
}

// Tenant & Organization Management
export interface Tenant {
  id: string;
  name: string;
  slug: string;
  logo?: string;
  createdAt: string;
  plan: 'free' | 'pro' | 'enterprise';
  members: number;
}

// Project Management
export type ProjectType = 'agentic-ai' | 'rag-pipeline' | 'llm-application' | 'chatbot' | 'custom';
export type DataSourceType = 'log-upload' | 's3' | 'azure-blob' | 'gcs' | 'api' | 'sdk';
export type IntegrationStatus = 'connected' | 'disconnected' | 'pending' | 'error';

export interface DataSource {
  id: string;
  type: DataSourceType;
  name: string;
  status: IntegrationStatus;
  connectedAt?: string;
  lastSync?: string;
  config: Record<string, any>;
}

export interface Project {
  id: string;
  tenantId: string;
  name: string;
  description: string;
  type: ProjectType;
  createdAt: string;
  updatedAt: string;
  dataSources: DataSource[];
  evaluationCount: number;
  status: 'active' | 'paused' | 'archived';
  tags: string[];
  team: string[];
}
