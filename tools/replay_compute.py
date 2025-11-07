#!/usr/bin/env python3
"""
RAIA Replay & Compute Tool

Deterministically compute metrics from event logs (NDJSON).
Features:
- Read from local files or S3
- Validate against schema
- Compute all canonical metrics
- Export to CSV/Parquet
- Exit non-zero on threshold violations (for CI/CD gates)
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

import pandas as pd
import jsonschema

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsComputer:
    """Compute all canonical metrics from events."""

    def __init__(self, events: List[Dict[str, Any]], metrics_config: Dict[str, Any]):
        self.events = events
        self.metrics_config = metrics_config
        self.sessions = defaultdict(list)
        self.results = {}

        # Group events by session
        for event in events:
            session_id = event.get('session_id')
            if session_id:
                self.sessions[session_id].append(event)

    def compute_all(self) -> Dict[str, Any]:
        """Compute all metrics."""
        logger.info(f"Computing metrics for {len(self.events)} events across {len(self.sessions)} sessions")

        metrics = {}

        # Task Success Rate
        metrics['task_success_rate'] = self._task_success_rate()

        # Escalation Rate
        metrics['escalation_rate'] = self._escalation_rate()

        # Safety Violation Rate
        metrics['safety_violation_rate'] = self._safety_violation_rate()

        # Constraint Adherence Rate
        metrics['constraint_adherence_rate'] = self._constraint_adherence_rate()

        # Grounded Claim Ratio
        metrics['grounded_claim_ratio'] = self._grounded_claim_ratio()

        # Evidence Missing Rate
        metrics['evidence_missing_rate'] = self._evidence_missing_rate()

        # Wrong Tool Rate
        metrics['wrong_tool_rate'] = self._wrong_tool_rate()

        # Redundant Call Rate
        metrics['redundant_call_rate'] = self._redundant_call_rate()

        # Backtrack Rate
        metrics['backtrack_rate'] = self._backtrack_rate()

        # Average Plan Depth
        metrics['avg_plan_depth'] = self._avg_plan_depth()

        # Plan Revision Rate
        metrics['plan_revision_rate'] = self._plan_revision_rate()

        # Latency Metrics
        metrics['e2e_latency_p50'], metrics['e2e_latency_p95'] = self._e2e_latency()

        # Token Efficiency
        metrics['token_efficiency'] = self._token_efficiency()

        # Cost per Success
        metrics['cost_per_success'] = self._cost_per_success()

        # Retry Rate
        metrics['retry_rate'] = self._retry_rate()

        # Error Rate
        metrics['error_rate'] = self._error_rate()

        # Observability Coverage
        metrics['observability_coverage'] = self._observability_coverage()

        return metrics

    def _filter_events(self, event_type: str) -> List[Dict]:
        """Filter events by type."""
        return [e for e in self.events if e.get('event') == event_type]

    def _task_success_rate(self) -> float:
        """Task Success Rate."""
        finalized = self._filter_events('finalized')
        if not finalized:
            return 0.0
        successful = [e for e in finalized if e.get('success') and e.get('constraints_met', True)]
        return (len(successful) / len(finalized)) * 100

    def _escalation_rate(self) -> float:
        """Escalation Rate."""
        sessions_with_escalation = set(e['session_id'] for e in self._filter_events('escalation'))
        sessions_with_finalized = set(e['session_id'] for e in self._filter_events('finalized'))
        if not sessions_with_finalized:
            return 0.0
        return (len(sessions_with_escalation) / len(sessions_with_finalized)) * 100

    def _safety_violation_rate(self) -> float:
        """Safety Violation Rate."""
        policy_flags = self._filter_events('policy_flag')
        violations = [e for e in policy_flags if e.get('severity') in ['violation', 'critical']]
        sessions_with_violations = set(e['session_id'] for e in violations)
        sessions_with_finalized = set(e['session_id'] for e in self._filter_events('finalized'))
        if not sessions_with_finalized:
            return 0.0
        return (len(sessions_with_violations) / len(sessions_with_finalized)) * 100

    def _constraint_adherence_rate(self) -> float:
        """Constraint Adherence Rate."""
        finalized = self._filter_events('finalized')
        if not finalized:
            return 0.0
        adhered = [e for e in finalized if e.get('constraints_met', True)]
        return (len(adhered) / len(finalized)) * 100

    def _grounded_claim_ratio(self) -> float:
        """Grounded Claim Ratio."""
        observations = self._filter_events('observation')
        if not observations:
            return 0.0
        grounded = [e for e in observations if e.get('grounded')]
        return (len(grounded) / len(observations)) * 100

    def _evidence_missing_rate(self) -> float:
        """Evidence Missing Rate."""
        observations = [e for e in self._filter_events('observation') if e.get('success')]
        if not observations:
            return 0.0
        missing = [e for e in observations if not e.get('grounded')]
        return (len(missing) / len(observations)) * 100

    def _wrong_tool_rate(self) -> float:
        """Wrong Tool Selection Rate."""
        tool_calls = [e for e in self._filter_events('tool_call') if e.get('expected_tool')]
        if not tool_calls:
            return 0.0
        wrong = [e for e in tool_calls if e.get('tool_name') != e.get('expected_tool')]
        return (len(wrong) / len(tool_calls)) * 100

    def _redundant_call_rate(self) -> float:
        """Redundant Tool Call Rate."""
        tool_calls = self._filter_events('tool_call')
        if not tool_calls:
            return 0.0

        # Group by session and check for duplicates
        redundant_count = 0
        for session_id, session_events in self.sessions.items():
            session_tools = [e for e in session_events if e.get('event') == 'tool_call']
            seen = set()
            for tool in session_tools:
                key = (tool.get('tool_name'), json.dumps(tool.get('tool_args', {}), sort_keys=True))
                if key in seen:
                    redundant_count += 1
                else:
                    seen.add(key)

        return (redundant_count / len(tool_calls)) * 100

    def _backtrack_rate(self) -> float:
        """Backtrack Rate."""
        corrections = [e for e in self._filter_events('correction') if e.get('correction_type') == 'backtrack']
        sessions_with_backtrack = set(e['session_id'] for e in corrections)
        sessions_with_finalized = set(e['session_id'] for e in self._filter_events('finalized'))
        if not sessions_with_finalized:
            return 0.0
        return (len(sessions_with_backtrack) / len(sessions_with_finalized)) * 100

    def _avg_plan_depth(self) -> float:
        """Average Plan Depth."""
        plans = [e for e in self._filter_events('plan_created') if e.get('revision_count') == 0]
        if not plans:
            return 0.0
        total_depth = sum(e.get('plan_depth', 0) for e in plans)
        return total_depth / len(plans)

    def _plan_revision_rate(self) -> float:
        """Plan Revision Rate."""
        revised_plans = [e for e in self._filter_events('plan_created') if e.get('revision_count', 0) > 0]
        sessions_with_revised = set(e['session_id'] for e in revised_plans)
        sessions_with_plans = set(e['session_id'] for e in self._filter_events('plan_created'))
        if not sessions_with_plans:
            return 0.0
        return (len(sessions_with_revised) / len(sessions_with_plans)) * 100

    def _e2e_latency(self) -> tuple:
        """End-to-End Latency (p50, p95)."""
        latencies = []
        for session_id, session_events in self.sessions.items():
            start_event = next((e for e in session_events if e.get('event') == 'session_start'), None)
            final_event = next((e for e in session_events if e.get('event') == 'finalized'), None)

            if start_event and final_event:
                start_ts = datetime.fromisoformat(start_event['ts'].replace('Z', '+00:00'))
                final_ts = datetime.fromisoformat(final_event['ts'].replace('Z', '+00:00'))
                latency_ms = (final_ts - start_ts).total_seconds() * 1000
                latencies.append(latency_ms)

        if not latencies:
            return 0.0, 0.0

        df = pd.Series(latencies)
        return df.quantile(0.50), df.quantile(0.95)

    def _token_efficiency(self) -> float:
        """Token Efficiency (avg tokens per success)."""
        total_tokens = sum(
            e.get('token_usage', {}).get('total_tokens', 0)
            for e in self.events
            if 'token_usage' in e
        )
        successful = [e for e in self._filter_events('finalized') if e.get('success')]
        if not successful:
            return 0.0
        return total_tokens / len(successful)

    def _cost_per_success(self) -> float:
        """Cost per Success (USD)."""
        total_cost = sum(e.get('cost', 0) for e in self.events if 'cost' in e)
        successful = [e for e in self._filter_events('finalized') if e.get('success')]
        if not successful:
            return 0.0
        return total_cost / len(successful)

    def _retry_rate(self) -> float:
        """Retry Rate."""
        tool_calls = self._filter_events('tool_call')
        if not tool_calls:
            return 0.0
        retries = [e for e in tool_calls if e.get('is_retry')]
        return (len(retries) / len(tool_calls)) * 100

    def _error_rate(self) -> float:
        """Error Rate (unrecoverable)."""
        errors = [e for e in self._filter_events('error') if not e.get('recoverable', True)]
        sessions_with_errors = set(e['session_id'] for e in errors)
        all_sessions = set(e['session_id'] for e in self._filter_events('session_start'))
        if not all_sessions:
            return 0.0
        return (len(sessions_with_errors) / len(all_sessions)) * 100

    def _observability_coverage(self) -> float:
        """Observability Coverage."""
        finalized = self._filter_events('finalized')
        if not finalized:
            return 0.0

        total_coverage = 0
        for final in finalized:
            total_steps = final.get('total_steps', 0)
            if total_steps == 0:
                continue

            session_id = final['session_id']
            session_events = [e for e in self.sessions[session_id] if e.get('event') != 'session_start']
            coverage = (len(session_events) / total_steps) * 100
            total_coverage += coverage

        return total_coverage / len(finalized) if finalized else 0.0


def load_events(input_path: str, schema_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load and validate events from NDJSON file or S3."""
    logger.info(f"Loading events from {input_path}")

    events = []

    # Load schema if provided
    schema = None
    if schema_path:
        with open(schema_path) as f:
            schema = json.load(f)

    # Handle S3 paths (simplified - in production use boto3)
    if input_path.startswith('s3://'):
        raise NotImplementedError("S3 support requires boto3 - implement if needed")

    # Load from local file
    path = Path(input_path)
    if not path.exists():
        logger.error(f"File not found: {input_path}")
        sys.exit(1)

    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)

                # Validate against schema
                if schema:
                    try:
                        jsonschema.validate(event, schema)
                    except jsonschema.ValidationError as e:
                        logger.warning(f"Line {line_num}: Schema validation failed: {e.message}")
                        continue

                events.append(event)

            except json.JSONDecodeError as e:
                logger.warning(f"Line {line_num}: Invalid JSON: {e}")
                continue

    logger.info(f"Loaded {len(events)} valid events")
    return events


def check_thresholds(metrics: Dict[str, float], config: Dict[str, Any]) -> List[str]:
    """Check if metrics violate configured thresholds."""
    violations = []

    for metric_def in config.get('metrics', []):
        metric_id = metric_def['id']
        value = metrics.get(metric_id)

        if value is None:
            continue

        thresholds = metric_def.get('thresholds', {})
        if not thresholds:
            continue

        critical = thresholds.get('critical', {})
        if critical:
            operator = critical['operator']
            threshold = critical['value']

            violated = False
            if operator == '<' and value < threshold:
                violated = True
            elif operator == '<=' and value <= threshold:
                violated = True
            elif operator == '>' and value > threshold:
                violated = True
            elif operator == '>=' and value >= threshold:
                violated = True
            elif operator == '==' and value == threshold:
                violated = True

            if violated:
                violations.append(f"{metric_id}: {value:.2f} (threshold: {operator} {threshold})")

    return violations


def main():
    parser = argparse.ArgumentParser(description='RAIA Replay & Compute Tool')
    parser.add_argument('input', help='Input NDJSON file or S3 path')
    parser.add_argument('--output-csv', default='metrics.csv', help='Output CSV file')
    parser.add_argument('--output-parquet', help='Output Parquet file (optional)')
    parser.add_argument('--schema', help='Path to event_schema.json for validation')
    parser.add_argument('--metrics-config', required=True, help='Path to metrics_config.json')
    parser.add_argument('--fail-on-threshold', action='store_true', help='Exit non-zero if thresholds violated')
    parser.add_argument('--group-by', default='agent_id', help='Group metrics by field (agent_id, tenant, project)')

    args = parser.parse_args()

    # Load events
    events = load_events(args.input, args.schema)

    if not events:
        logger.error("No valid events found")
        sys.exit(1)

    # Load metrics config
    with open(args.metrics_config) as f:
        metrics_config = json.load(f)

    # Compute metrics
    computer = MetricsComputer(events, metrics_config)
    metrics = computer.compute_all()

    # Print metrics
    logger.info("\n=== Computed Metrics ===")
    for name, value in metrics.items():
        if isinstance(value, float):
            logger.info(f"{name}: {value:.2f}")
        else:
            logger.info(f"{name}: {value}")

    # Export to CSV
    df = pd.DataFrame([metrics])
    df.to_csv(args.output_csv, index=False)
    logger.info(f"\nMetrics exported to {args.output_csv}")

    # Export to Parquet if requested
    if args.output_parquet:
        df.to_parquet(args.output_parquet, index=False)
        logger.info(f"Metrics exported to {args.output_parquet}")

    # Check thresholds
    if args.fail_on_threshold:
        violations = check_thresholds(metrics, metrics_config)
        if violations:
            logger.error("\n=== THRESHOLD VIOLATIONS ===")
            for violation in violations:
                logger.error(violation)
            sys.exit(1)
        else:
            logger.info("\n=== All thresholds passed ===")

    sys.exit(0)


if __name__ == '__main__':
    main()
