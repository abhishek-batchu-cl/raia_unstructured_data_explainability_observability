/**
 * TypeScript type definitions for RAIA events.
 * Mirrors the JSON schema in event_schema.json
 */

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface EvidenceRef {
  source: string;
  id: string;
  relevance_score?: number;
}

export type PolicyTag =
  | 'pii'
  | 'phi'
  | 'financial'
  | 'confidential'
  | 'public'
  | 'internal'
  | 'safety_critical'
  | 'regulatory'
  | 'audit_required';

export interface RedactionMetadata {
  applied: boolean;
  fields: string[];
  rule_ids: string[];
}

export interface Env {
  sdk_version: string;
  schema_version: string;
  llm?: string;
  llm_version?: string;
  seed?: number;
  temperature?: number;
  tenant: string;
  project: string;
  region?: string;
  deployment?: 'dev' | 'staging' | 'prod';
}

export interface BaseEvent {
  event: string;
  event_id: string;
  ts: string;
  session_id: string;
  run_id: string;
  agent_id: string;
  graph_node?: string;
  parent_event_id?: string;
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  latency_ms?: number;
  token_usage?: TokenUsage;
  cost?: number;
  evidence_refs?: EvidenceRef[];
  policy_tags?: PolicyTag[];
  redaction?: RedactionMetadata;
  env: Env;
  _signature?: string;
}

export interface SessionStartEvent extends BaseEvent {
  event: 'session_start';
  user_id: string;
  task: string;
  domain: 'healthcare' | 'insurance' | 'banking' | 'retail' | 'public_sector' | 'general';
  constraints?: string[];
}

export interface PlanCreatedEvent extends BaseEvent {
  event: 'plan_created';
  plan: {
    steps: Array<{
      id: string;
      description: string;
      tool?: string;
      dependencies?: string[];
    }>;
    rationale?: string;
  };
  plan_depth: number;
  revision_count: number;
}

export interface ToolCallEvent extends BaseEvent {
  event: 'tool_call';
  tool_name: string;
  tool_args: Record<string, any>;
  expected_tool?: string;
  is_retry: boolean;
  retry_count: number;
}

export interface ObservationEvent extends BaseEvent {
  event: 'observation';
  observation: string;
  success: boolean;
  error_type?: 'timeout' | 'auth' | 'rate_limit' | 'validation' | 'server_error' | 'not_found' | 'other';
  grounded?: boolean;
}

export interface CritiqueEvent extends BaseEvent {
  event: 'critique';
  critique_text: string;
  issues: Array<{
    type: 'factual_error' | 'missing_evidence' | 'constraint_violation' | 'wrong_tool' | 'incomplete' | 'inefficiency';
    description: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }>;
}

export interface CorrectionEvent extends BaseEvent {
  event: 'correction';
  correction_type: 'backtrack' | 'replan' | 'retry_tool' | 'add_evidence' | 'refine_output';
  corrected_event_id: string;
  reason: string;
}

export interface EscalationEvent extends BaseEvent {
  event: 'escalation';
  escalation_reason: 'uncertainty' | 'safety_concern' | 'constraint_violation' | 'missing_capability' | 'timeout' | 'high_stakes';
  escalation_target: 'human' | 'supervisor_agent' | 'expert_agent';
  context: string;
}

export interface FinalizedEvent extends BaseEvent {
  event: 'finalized';
  final_answer?: string;
  success: boolean;
  constraints_met?: boolean;
  total_steps?: number;
  total_tool_calls?: number;
}

export interface ErrorEvent extends BaseEvent {
  event: 'error';
  error_type: 'llm_error' | 'tool_error' | 'validation_error' | 'timeout' | 'resource_exhausted' | 'internal_error';
  error_message: string;
  recoverable?: boolean;
  stack_trace?: string;
}

export interface PolicyFlagEvent extends BaseEvent {
  event: 'policy_flag';
  policy_id: string;
  severity: 'info' | 'warning' | 'violation' | 'critical';
  description: string;
  violated_event_id?: string;
  auto_action?: 'none' | 'flag' | 'block' | 'redact' | 'escalate';
}

export type RAIAEvent =
  | SessionStartEvent
  | PlanCreatedEvent
  | ToolCallEvent
  | ObservationEvent
  | CritiqueEvent
  | CorrectionEvent
  | EscalationEvent
  | FinalizedEvent
  | ErrorEvent
  | PolicyFlagEvent;
