"""
RAIA Comparison & Reporting Utilities

Utilities for comparing runs, generating reports, and benchmarking.
"""

import statistics
from typing import List, Optional
from datetime import datetime

from raia.storage.base import BaseRAIAStorage
from raia.models_comparison import RunComparison, EvaluationReport


class RAIAComparator:
    """
    Utility for comparing RAG system runs and generating reports.

    Enables A/B testing, benchmarking, and performance analysis across runs.
    """

    def __init__(self, storage: BaseRAIAStorage):
        """
        Initialize comparator with storage backend.

        Args:
            storage: Storage backend for retrieving run data
        """
        self.storage = storage

    def compare_runs(
        self,
        run_ids: List[str],
        comparison_name: Optional[str] = None,
    ) -> RunComparison:
        """
        Compare multiple runs side-by-side.

        Args:
            run_ids: List of run IDs to compare
            comparison_name: Optional name for this comparison

        Returns:
            RunComparison with detailed comparison results
        """
        if len(run_ids) < 2:
            raise ValueError("Need at least 2 runs to compare")

        # Collect metrics for each run
        run_metrics = {}
        for run_id in run_ids:
            # Get answer quality metrics
            quality_metrics = self.storage.get_answer_quality_for_run(run_id)
            if not quality_metrics:
                raise ValueError(f"No quality metrics found for run {run_id}")

            # Calculate averages (overall quality from relevance and completeness)
            qualities = []
            for m in quality_metrics:
                # Calculate overall quality from available metrics
                metrics_used = []
                if m.answer_relevance is not None:
                    metrics_used.append(m.answer_relevance)
                if m.answer_completeness is not None:
                    metrics_used.append(m.answer_completeness)
                if m.answer_faithfulness is not None:
                    metrics_used.append(m.answer_faithfulness)

                overall = sum(metrics_used) / len(metrics_used) if metrics_used else 0.0
                qualities.append(overall)

            latencies = [m.generation_latency_ms for m in quality_metrics if m.generation_latency_ms]
            # Extract cost from metadata if available
            costs = []
            for m in quality_metrics:
                if m.metadata and "cost_usd" in m.metadata:
                    costs.append(m.metadata["cost_usd"])

            run_metrics[run_id] = {
                "avg_quality": statistics.mean(qualities) if qualities else 0.0,
                "avg_latency": statistics.mean(latencies) if latencies else 0.0,
                "avg_cost": statistics.mean(costs) if costs else 0.0,
            }

        # Extract metrics dictionaries
        avg_quality = {rid: m["avg_quality"] for rid, m in run_metrics.items()}
        avg_latency_ms = {rid: m["avg_latency"] for rid, m in run_metrics.items()}
        avg_cost_usd = {rid: m["avg_cost"] for rid, m in run_metrics.items()}

        # Determine winners
        best_quality_run = max(avg_quality, key=avg_quality.get)
        best_latency_run = min(avg_latency_ms, key=avg_latency_ms.get)
        best_cost_run = min(avg_cost_usd, key=avg_cost_usd.get)

        # Overall winner (simple heuristic: best quality with acceptable cost)
        quality_scores = {rid: avg_quality[rid] for rid in run_ids}
        cost_normalized = {
            rid: 1 - (avg_cost_usd[rid] / max(avg_cost_usd.values()))
            for rid in run_ids
        }
        combined_scores = {
            rid: quality_scores[rid] * 0.7 + cost_normalized[rid] * 0.3
            for rid in run_ids
        }
        overall_winner = max(combined_scores, key=combined_scores.get)

        # Winner rationale
        winner_quality = avg_quality[overall_winner]
        winner_cost = avg_cost_usd[overall_winner]
        winner_latency = avg_latency_ms[overall_winner]

        if overall_winner == best_quality_run and overall_winner == best_cost_run:
            rationale = f"Best in both quality ({winner_quality:.2%}) and cost (${winner_cost:.6f})"
        elif overall_winner == best_quality_run:
            rationale = f"Highest quality ({winner_quality:.2%}) justifies cost"
        else:
            rationale = f"Best balance of quality ({winner_quality:.2%}) and cost (${winner_cost:.6f})"

        # Calculate variances
        quality_variance = statistics.variance(avg_quality.values()) if len(avg_quality) > 1 else 0.0
        latency_variance = statistics.variance(avg_latency_ms.values()) if len(avg_latency_ms) > 1 else 0.0
        cost_variance = statistics.variance(avg_cost_usd.values()) if len(avg_cost_usd) > 1 else 0.0

        return RunComparison(
            comparison_name=comparison_name or f"Comparison of {len(run_ids)} runs",
            run_ids=run_ids,
            avg_quality=avg_quality,
            avg_latency_ms=avg_latency_ms,
            avg_cost_usd=avg_cost_usd,
            best_quality_run=best_quality_run,
            best_latency_run=best_latency_run,
            best_cost_run=best_cost_run,
            overall_winner=overall_winner,
            winner_rationale=rationale,
            quality_variance=quality_variance,
            latency_variance=latency_variance,
            cost_variance=cost_variance,
        )

    def generate_report(
        self,
        run_ids: List[str],
        report_name: Optional[str] = None,
    ) -> EvaluationReport:
        """
        Generate comprehensive evaluation report for one or more runs.

        Args:
            run_ids: List of run IDs to include in report
            report_name: Optional report name

        Returns:
            EvaluationReport with comprehensive analysis
        """
        all_quality_metrics = []
        all_attribution_maps = []

        for run_id in run_ids:
            quality_metrics = self.storage.get_answer_quality_for_run(run_id)
            all_quality_metrics.extend(quality_metrics)

            attribution_maps = self.storage.get_attribution_maps_for_run(run_id)
            all_attribution_maps.extend(attribution_maps)

        if not all_quality_metrics:
            raise ValueError("No quality metrics found for any run")

        # Calculate summary metrics
        total_queries = len(all_quality_metrics)

        # Calculate overall quality for each metric
        qualities = []
        for m in all_quality_metrics:
            metrics_used = []
            if m.answer_relevance is not None:
                metrics_used.append(m.answer_relevance)
            if m.answer_completeness is not None:
                metrics_used.append(m.answer_completeness)
            if m.answer_faithfulness is not None:
                metrics_used.append(m.answer_faithfulness)

            overall = sum(metrics_used) / len(metrics_used) if metrics_used else 0.0
            qualities.append(overall)

        latencies = [m.generation_latency_ms for m in all_quality_metrics if m.generation_latency_ms]

        # Extract costs from metadata
        costs = []
        for m in all_quality_metrics:
            if m.metadata and "cost_usd" in m.metadata:
                costs.append(m.metadata["cost_usd"])

        avg_quality = statistics.mean(qualities)
        avg_latency_ms = statistics.mean(latencies) if latencies else 0.0
        avg_cost_usd = statistics.mean(costs) if costs else 0.0

        # Quality breakdown
        quality_excellent = sum(1 for q in qualities if q >= 0.9)
        quality_good = sum(1 for q in qualities if 0.7 <= q < 0.9)
        quality_poor = sum(1 for q in qualities if q < 0.7)

        # Explainability metrics
        avg_faithfulness = None
        avg_hallucination = None
        if all_attribution_maps:
            faithfulness_scores = [m.faithfulness_score for m in all_attribution_maps]
            hallucination_scores = [m.hallucination_score for m in all_attribution_maps]
            avg_faithfulness = statistics.mean(faithfulness_scores)
            avg_hallucination = statistics.mean(hallucination_scores)

        # Generate insights
        strengths = []
        weaknesses = []
        recommendations = []

        # Analyze strengths
        if avg_quality >= 0.9:
            strengths.append(f"Excellent quality ({avg_quality:.2%})")
        elif avg_quality >= 0.8:
            strengths.append(f"Good quality ({avg_quality:.2%})")

        if avg_faithfulness and avg_faithfulness >= 0.95:
            strengths.append(f"High faithfulness ({avg_faithfulness:.2%})")

        if avg_hallucination and avg_hallucination <= 0.05:
            strengths.append(f"Low hallucination rate ({avg_hallucination:.2%})")

        if quality_excellent / total_queries >= 0.7:
            strengths.append(f"Consistent excellence ({quality_excellent}/{total_queries} queries)")

        # Analyze weaknesses
        if avg_quality < 0.8:
            weaknesses.append(f"Quality below target ({avg_quality:.2%})")

        if quality_poor / total_queries >= 0.1:
            weaknesses.append(f"High poor-quality rate ({quality_poor}/{total_queries} queries)")

        if avg_latency_ms > 2000:
            weaknesses.append(f"High average latency ({avg_latency_ms:.0f}ms)")

        if avg_cost_usd > 0.01:
            weaknesses.append(f"High cost per query (${avg_cost_usd:.4f})")

        # Generate recommendations
        if quality_poor > 0:
            recommendations.append(f"Investigate {quality_poor} poor-quality queries")

        if avg_latency_ms > 2000:
            recommendations.append("Optimize pipeline to reduce latency")

        if avg_cost_usd > 0.005:
            recommendations.append("Consider cost optimization strategies")

        if avg_hallucination and avg_hallucination > 0.1:
            recommendations.append("Improve retrieval to reduce hallucinations")

        return EvaluationReport(
            report_name=report_name or f"Evaluation Report - {datetime.utcnow().strftime('%Y-%m-%d')}",
            run_ids=run_ids,
            total_queries=total_queries,
            avg_quality=avg_quality,
            avg_latency_ms=avg_latency_ms,
            avg_cost_usd=avg_cost_usd,
            quality_excellent=quality_excellent,
            quality_good=quality_good,
            quality_poor=quality_poor,
            avg_faithfulness=avg_faithfulness,
            avg_hallucination=avg_hallucination,
            optimization_opportunities=len(recommendations),
            potential_annual_savings_usd=None,  # Would need what-if analysis
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

    def print_comparison(self, comparison: RunComparison) -> None:
        """Print formatted comparison results."""
        print(f"\n{'='*80}")
        print(f"  {comparison.comparison_name}")
        print(f"{'='*80}\n")

        print(f"Comparing {len(comparison.run_ids)} runs:\n")

        # Print metrics table
        print(f"{'Run ID':<30} {'Quality':>12} {'Latency':>12} {'Cost':>12}")
        print("-" * 80)
        for run_id in comparison.run_ids:
            quality = comparison.avg_quality[run_id]
            latency = comparison.avg_latency_ms[run_id]
            cost = comparison.avg_cost_usd[run_id]

            # Add winner badges
            badges = []
            if run_id == comparison.best_quality_run:
                badges.append("👑Q")
            if run_id == comparison.best_latency_run:
                badges.append("⚡L")
            if run_id == comparison.best_cost_run:
                badges.append("💰C")

            badge_str = " ".join(badges) if badges else ""
            run_display = f"{run_id[:28]:<28} {badge_str}"

            print(f"{run_display:<30} {quality:>11.2%} {latency:>10.0f}ms ${cost:>10.6f}")

        print("\nWinners:")
        print(f"  👑 Best Quality:  {comparison.best_quality_run}")
        print(f"  ⚡ Best Latency:  {comparison.best_latency_run}")
        print(f"  💰 Best Cost:     {comparison.best_cost_run}")
        print(f"\n  🏆 Overall Winner: {comparison.overall_winner}")
        print(f"     {comparison.winner_rationale}")

    def print_report(self, report: EvaluationReport) -> None:
        """Print formatted evaluation report."""
        print(f"\n{'='*80}")
        print(f"  {report.report_name}")
        print(f"{'='*80}\n")

        print(f"Runs evaluated: {', '.join(report.run_ids)}\n")

        print("Summary Metrics:")
        print(f"  Total queries:    {report.total_queries}")
        print(f"  Average quality:  {report.avg_quality:.2%}")
        print(f"  Average latency:  {report.avg_latency_ms:.0f}ms")
        print(f"  Average cost:     ${report.avg_cost_usd:.6f}")

        print("\nQuality Breakdown:")
        print(f"  Excellent (≥90%): {report.quality_excellent} ({report.quality_excellent/report.total_queries:.1%})")
        print(f"  Good (70-90%):    {report.quality_good} ({report.quality_good/report.total_queries:.1%})")
        print(f"  Poor (<70%):      {report.quality_poor} ({report.quality_poor/report.total_queries:.1%})")

        if report.avg_faithfulness:
            print("\nExplainability Metrics:")
            print(f"  Faithfulness:     {report.avg_faithfulness:.2%}")
            print(f"  Hallucination:    {report.avg_hallucination:.2%}")

        if report.strengths:
            print("\nStrengths:")
            for strength in report.strengths:
                print(f"  ✅ {strength}")

        if report.weaknesses:
            print("\nWeaknesses:")
            for weakness in report.weaknesses:
                print(f"  ⚠️  {weakness}")

        if report.recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
