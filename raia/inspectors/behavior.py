"""
RAIA Inspectors - Behavior Inspector

Detects behavioral patterns in LangGraph executions:
- Loops / repeated node sequences
- Redundant tool usage
- Suboptimal paths
- State inconsistencies
"""

import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from raia.inspectors.base import RAIAInspectorBase
from raia.storage.base import BaseRAIAStorage


logger = logging.getLogger(__name__)


class RAIABehaviorInspector(RAIAInspectorBase):
    """
    Analyzes LangGraph execution patterns to detect behavioral issues.

    NOT a callback handler - processes LangGraph stream events manually.

    Detects:
    - Loop patterns (repeated node sequences)
    - Redundant tool usage (same tool with similar inputs)
    - Suboptimal paths (too many nodes for simple queries)
    - State inconsistencies (conflicting state values)

    Usage:
        inspector = RAIABehaviorInspector()

        for event in graph.stream(input, stream_mode="updates"):
            inspector.process_event(run_id, event)

        inspector.finalize_run(run_id)
    """

    def __init__(
        self,
        storage: Optional[BaseRAIAStorage] = None,
        loop_threshold: int = 3,
        redundancy_window_seconds: float = 30.0,
        suboptimal_path_threshold: int = 10
    ):
        """
        Initialize behavior inspector.

        Args:
            storage: Storage backend (uses global config if None)
            loop_threshold: Number of repetitions to trigger loop detection
            redundancy_window_seconds: Time window for redundancy detection
            suboptimal_path_threshold: Number of nodes to trigger path warning
        """
        super().__init__(storage=storage)

        self.loop_threshold = loop_threshold
        self.redundancy_window_seconds = redundancy_window_seconds
        self.suboptimal_path_threshold = suboptimal_path_threshold

        # Per-run state tracking
        self._run_state: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "node_sequence": [],
            "node_counts": defaultdict(int),
            "tool_calls": [],  # List of (tool_name, args, timestamp)
            "state_snapshots": [],
            "total_nodes": 0
        })

    def process_event(self, run_id: str, event: Dict[str, Any]) -> None:
        """
        Process a LangGraph stream event.

        Args:
            run_id: Unique run identifier
            event: Event dictionary from graph.stream()
        """
        state = self._run_state[run_id]

        # Extract node name and data from event
        # LangGraph events typically have structure: {node_name: {data}}
        for node_name, node_data in event.items():
            if node_name.startswith("__"):
                # Skip internal nodes
                continue

            # Track node sequence
            state["node_sequence"].append(node_name)
            state["node_counts"][node_name] += 1
            state["total_nodes"] += 1

            # Detect loops
            self._detect_loops(run_id, node_name, state)

            # Detect redundant tool calls
            if "tool_calls" in node_data or "tool" in node_name.lower():
                self._detect_redundant_tools(run_id, node_name, node_data, state)

            # Track state snapshots for inconsistency detection
            if isinstance(node_data, dict):
                state["state_snapshots"].append({
                    "node": node_name,
                    "timestamp": datetime.utcnow(),
                    "data": node_data
                })

            logger.debug(f"Processed event for node {node_name} in run {run_id}")

    def _detect_loops(self, run_id: str, current_node: str, state: Dict[str, Any]) -> None:
        """Detect loop patterns in node sequences."""
        sequence = state["node_sequence"]

        # Check for simple repetition
        if state["node_counts"][current_node] >= self.loop_threshold:
            self._save_signal(
                run_id=run_id,
                signal_type="loop_detected",
                severity="high",
                message=f"Node '{current_node}' executed {state['node_counts'][current_node]} times",
                node_name=current_node,
                metadata={"count": state["node_counts"][current_node]}
            )

        # Check for cyclic patterns (e.g., A -> B -> C -> A -> B -> C)
        if len(sequence) >= 6:
            # Look for repeating subsequences
            for cycle_len in range(2, 6):
                if len(sequence) >= cycle_len * 2:
                    recent = sequence[-(cycle_len * 2):]
                    first_half = recent[:cycle_len]
                    second_half = recent[cycle_len:]
                    if first_half == second_half:
                        self._save_signal(
                            run_id=run_id,
                            signal_type="loop_detected",
                            severity="medium",
                            message=f"Cyclic pattern detected: {' -> '.join(first_half)} repeated",
                            metadata={
                                "pattern": first_half,
                                "cycle_length": cycle_len
                            }
                        )
                        break

    def _detect_redundant_tools(
        self,
        run_id: str,
        node_name: str,
        node_data: Dict[str, Any],
        state: Dict[str, Any]
    ) -> None:
        """Detect redundant tool usage."""
        # Extract tool call info
        tool_name = node_data.get("tool_name") or node_name
        tool_args = node_data.get("tool_args", {})
        timestamp = datetime.utcnow()

        # Add to tool calls
        state["tool_calls"].append((tool_name, tool_args, timestamp))

        # Check for redundancy in recent window
        cutoff_time = timestamp.timestamp() - self.redundancy_window_seconds
        recent_calls = [
            (name, args, ts)
            for name, args, ts in state["tool_calls"]
            if ts.timestamp() > cutoff_time and name == tool_name
        ]

        if len(recent_calls) >= 3:
            # Check if arguments are similar (simple string comparison)
            args_strs = [str(args) for _, args, _ in recent_calls]
            if len(set(args_strs)) <= 2:  # Only 1-2 unique argument sets
                self._save_signal(
                    run_id=run_id,
                    signal_type="redundant_tool_use",
                    severity="medium",
                    message=f"Tool '{tool_name}' called {len(recent_calls)} times with similar arguments within {self.redundancy_window_seconds}s",
                    node_name=node_name,
                    metadata={
                        "tool_name": tool_name,
                        "call_count": len(recent_calls),
                        "window_seconds": self.redundancy_window_seconds
                    }
                )

    def _detect_state_inconsistencies(self, run_id: str, state: Dict[str, Any]) -> None:
        """Detect inconsistencies in state snapshots."""
        snapshots = state["state_snapshots"]
        if len(snapshots) < 2:
            return

        # Look for conflicting values for the same key
        key_values: Dict[str, List[Any]] = defaultdict(list)

        for snapshot in snapshots:
            data = snapshot.get("data", {})
            if isinstance(data, dict):
                for key, value in data.items():
                    if not key.startswith("_"):  # Skip internal keys
                        key_values[key].append(value)

        # Check for inconsistencies
        for key, values in key_values.items():
            unique_values = set(str(v) for v in values)
            if len(unique_values) > 1 and len(values) > 2:
                # Value changed multiple times - could be normal or could indicate issue
                # Flag as low severity for awareness
                self._save_signal(
                    run_id=run_id,
                    signal_type="state_inconsistency",
                    severity="low",
                    message=f"State key '{key}' changed {len(unique_values)} times across execution",
                    metadata={
                        "key": key,
                        "value_count": len(unique_values),
                        "total_changes": len(values)
                    }
                )

    def finalize_run(self, run_id: str) -> None:
        """
        Finalize analysis for a run.

        Performs end-of-run analysis and cleanup.

        Args:
            run_id: Unique run identifier
        """
        state = self._run_state.get(run_id)
        if not state:
            logger.warning(f"No state found for run {run_id}")
            return

        # Check for suboptimal paths
        if state["total_nodes"] > self.suboptimal_path_threshold:
            self._save_signal(
                run_id=run_id,
                signal_type="suboptimal_path",
                severity="medium",
                message=f"Execution took {state['total_nodes']} nodes (threshold: {self.suboptimal_path_threshold})",
                metadata={
                    "total_nodes": state["total_nodes"],
                    "threshold": self.suboptimal_path_threshold,
                    "node_counts": dict(state["node_counts"])
                }
            )

        # Detect state inconsistencies
        self._detect_state_inconsistencies(run_id, state)

        # Check for info redundancy (same node producing similar output)
        # This is a simplified check
        unique_nodes = len(set(state["node_sequence"]))
        if state["total_nodes"] > unique_nodes * 2:
            self._save_signal(
                run_id=run_id,
                signal_type="info_redundancy",
                severity="low",
                message=f"High repetition: {state['total_nodes']} total steps but only {unique_nodes} unique nodes",
                metadata={
                    "total_nodes": state["total_nodes"],
                    "unique_nodes": unique_nodes,
                    "repetition_factor": state["total_nodes"] / unique_nodes
                }
            )

        logger.info(f"Finalized behavior analysis for run {run_id}: {state['total_nodes']} nodes processed")

        # Cleanup
        del self._run_state[run_id]

    def reset_run(self, run_id: str) -> None:
        """
        Clear internal state for a run.

        Args:
            run_id: Unique run identifier
        """
        if run_id in self._run_state:
            del self._run_state[run_id]
            logger.debug(f"Reset state for run {run_id}")
