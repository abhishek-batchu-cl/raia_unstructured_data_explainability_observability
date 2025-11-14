"""
Monitoring Module for RAIA Enterprise
======================================

Provides comprehensive monitoring with:
- Prometheus metrics
- Health checks
- Performance tracking
- Custom metrics
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Callable
import time
from functools import wraps

# ============================================================================
# Prometheus Metrics
# ============================================================================

# Request metrics
http_requests_total = Counter(
    "raia_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "raia_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

# Database metrics
db_query_duration_seconds = Histogram(
    "raia_db_query_duration_seconds",
    "Database query latency",
    ["table", "operation"]
)

db_connections_active = Gauge(
    "raia_db_connections_active",
    "Active database connections"
)

db_queries_total = Counter(
    "raia_db_queries_total",
    "Total database queries",
    ["table", "operation", "status"]
)

# RAIA-specific metrics
raia_runs_total = Counter(
    "raia_runs_total",
    "Total RAIA runs processed",
    ["status"]
)

raia_api_calls_total = Counter(
    "raia_api_calls_total",
    "Total API calls by endpoint",
    ["endpoint", "method"]
)

raia_retrieval_metrics_avg = Gauge(
    "raia_retrieval_metrics_avg",
    "Average retrieval metrics",
    ["metric_type"]  # precision, recall, f1, mrr, ndcg
)

raia_answer_quality_avg = Gauge(
    "raia_answer_quality_avg",
    "Average answer quality metrics",
    ["metric_type"]  # faithfulness, hallucination, relevance
)

raia_latency_ms = Histogram(
    "raia_latency_ms",
    "RAIA operation latency in milliseconds",
    ["operation_type"]
)

# Cache metrics
cache_hits_total = Counter(
    "raia_cache_hits_total",
    "Total cache hits"
)

cache_misses_total = Counter(
    "raia_cache_misses_total",
    "Total cache misses"
)

cache_size_bytes = Gauge(
    "raia_cache_size_bytes",
    "Current cache size in bytes"
)

# Authentication metrics
auth_attempts_total = Counter(
    "raia_auth_attempts_total",
    "Total authentication attempts",
    ["method", "status"]  # method: jwt/api_key, status: success/failure
)

auth_active_sessions = Gauge(
    "raia_auth_active_sessions",
    "Number of active sessions"
)

# System metrics
system_info = Info(
    "raia_system",
    "RAIA system information"
)

# Set system info
system_info.info({
    "version": "1.0.0",
    "environment": "production",
    "database": "sqlite"
})


# ============================================================================
# Metric Decorators
# ============================================================================

def track_request_metrics(endpoint: str):
    """
    Decorator to track HTTP request metrics.

    Usage:
        @app.get("/api/data")
        @track_request_metrics("/api/data")
        async def get_data():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            method = "GET"  # You can extract this from request
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                status = "success"
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status="200"
                ).inc()
                return result

            except Exception as e:
                status = "error"
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status="500"
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

        return wrapper
    return decorator


def track_db_query(table: str, operation: str):
    """
    Decorator to track database query metrics.

    Usage:
        @track_db_query("raia_runs", "SELECT")
        def get_runs():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                db_queries_total.labels(
                    table=table,
                    operation=operation,
                    status="success"
                ).inc()
                return result

            except Exception as e:
                db_queries_total.labels(
                    table=table,
                    operation=operation,
                    status="error"
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    table=table,
                    operation=operation
                ).observe(duration)

        return wrapper
    return decorator


# ============================================================================
# Monitoring Service
# ============================================================================

class MonitoringService:
    """Service for tracking RAIA-specific metrics."""

    @staticmethod
    def record_run(status: str):
        """Record a RAIA run."""
        raia_runs_total.labels(status=status).inc()

    @staticmethod
    def record_api_call(endpoint: str, method: str):
        """Record an API call."""
        raia_api_calls_total.labels(endpoint=endpoint, method=method).inc()

    @staticmethod
    def update_retrieval_metrics(metrics: dict):
        """Update average retrieval metrics."""
        for metric_type, value in metrics.items():
            raia_retrieval_metrics_avg.labels(metric_type=metric_type).set(value)

    @staticmethod
    def update_answer_quality(metrics: dict):
        """Update average answer quality metrics."""
        for metric_type, value in metrics.items():
            raia_answer_quality_avg.labels(metric_type=metric_type).set(value)

    @staticmethod
    def record_latency(operation_type: str, latency_ms: float):
        """Record operation latency."""
        raia_latency_ms.labels(operation_type=operation_type).observe(latency_ms)

    @staticmethod
    def record_cache_hit():
        """Record cache hit."""
        cache_hits_total.inc()

    @staticmethod
    def record_cache_miss():
        """Record cache miss."""
        cache_misses_total.inc()

    @staticmethod
    def update_cache_size(size_bytes: int):
        """Update cache size."""
        cache_size_bytes.set(size_bytes)

    @staticmethod
    def record_auth_attempt(method: str, status: str):
        """Record authentication attempt."""
        auth_attempts_total.labels(method=method, status=status).inc()

    @staticmethod
    def update_active_sessions(count: int):
        """Update active session count."""
        auth_active_sessions.set(count)

    @staticmethod
    def update_db_connections(count: int):
        """Update active database connections."""
        db_connections_active.set(count)


# ============================================================================
# Health Check System
# ============================================================================

from typing import Dict, List
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class HealthCheck:
    """Health check result."""

    def __init__(self, name: str, status: HealthStatus, message: str, details: dict = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details
        }


class HealthCheckService:
    """Comprehensive health check service."""

    def __init__(self):
        self.checks: List[Callable] = []

    def add_check(self, check: Callable):
        """Add a health check."""
        self.checks.append(check)

    async def run_all_checks(self) -> Dict:
        """Run all health checks."""
        results = []
        overall_status = HealthStatus.HEALTHY

        for check in self.checks:
            try:
                result = await check()
                results.append(result.to_dict())

                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

            except Exception as e:
                results.append({
                    "name": check.__name__,
                    "status": HealthStatus.UNHEALTHY,
                    "message": f"Check failed: {str(e)}",
                    "details": {}
                })
                overall_status = HealthStatus.UNHEALTHY

        return {
            "status": overall_status,
            "checks": results,
            "timestamp": time.time()
        }


# Default health checks
async def check_database() -> HealthCheck:
    """Check database connectivity."""
    try:
        import sqlite3
        conn = sqlite3.connect("data/demo_databases/complete_end_to_end_demo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()

        return HealthCheck(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection OK"
        )
    except Exception as e:
        return HealthCheck(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}"
        )


async def check_disk_space() -> HealthCheck:
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100

        if free_percent < 10:
            status = HealthStatus.UNHEALTHY
            message = f"Low disk space: {free_percent:.1f}% free"
        elif free_percent < 20:
            status = HealthStatus.DEGRADED
            message = f"Disk space warning: {free_percent:.1f}% free"
        else:
            status = HealthStatus.HEALTHY
            message = f"Disk space OK: {free_percent:.1f}% free"

        return HealthCheck(
            name="disk_space",
            status=status,
            message=message,
            details={
                "total_gb": total // (1024**3),
                "free_gb": free // (1024**3),
                "free_percent": free_percent
            }
        )
    except Exception as e:
        return HealthCheck(
            name="disk_space",
            status=HealthStatus.UNHEALTHY,
            message=f"Disk check failed: {str(e)}"
        )


async def check_memory() -> HealthCheck:
    """Check memory usage."""
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_percent = memory.available / memory.total * 100

        if available_percent < 10:
            status = HealthStatus.UNHEALTHY
            message = f"Low memory: {available_percent:.1f}% available"
        elif available_percent < 20:
            status = HealthStatus.DEGRADED
            message = f"Memory warning: {available_percent:.1f}% available"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory OK: {available_percent:.1f}% available"

        return HealthCheck(
            name="memory",
            status=status,
            message=message,
            details={
                "total_gb": memory.total // (1024**3),
                "available_gb": memory.available // (1024**3),
                "percent_used": memory.percent
            }
        )
    except ImportError:
        return HealthCheck(
            name="memory",
            status=HealthStatus.DEGRADED,
            message="Memory monitoring unavailable (install psutil)"
        )
    except Exception as e:
        return HealthCheck(
            name="memory",
            status=HealthStatus.UNHEALTHY,
            message=f"Memory check failed: {str(e)}"
        )


# Initialize health check service
health_service = HealthCheckService()
health_service.add_check(check_database)
health_service.add_check(check_disk_space)
health_service.add_check(check_memory)


# ============================================================================
# Metrics Endpoint Handler
# ============================================================================

async def metrics_endpoint() -> Response:
    """
    Prometheus metrics endpoint.

    Returns:
        Prometheus-formatted metrics
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    # Record some metrics
    MonitoringService.record_run("success")
    MonitoringService.record_api_call("/api/dashboard", "GET")
    MonitoringService.update_retrieval_metrics({
        "precision": 0.85,
        "recall": 0.78,
        "f1": 0.81
    })
    MonitoringService.record_latency("retrieval", 150.5)
    MonitoringService.record_cache_hit()

    # Print metrics
    print("\n=== Prometheus Metrics ===")
    print(generate_latest().decode('utf-8'))

    # Run health checks
    import asyncio
    health = asyncio.run(health_service.run_all_checks())
    print("\n=== Health Check ===")
    import json
    print(json.dumps(health, indent=2, default=str))
