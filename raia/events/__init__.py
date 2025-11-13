"""
Event Logging Components (RAIA Events)

Production-grade event emitter with:
- Async batching
- Circuit breaker pattern
- Multiple transports (file, HTTP, Kafka, OTLP)
- PII/PHI redaction
- HMAC signing for integrity
"""

from .emitter import EventEmitter, EmitterConfig, TransportType, CircuitState
from .redactor import Redactor, RedactionRule
from .signer import EventSigner

__all__ = [
    "EventEmitter",
    "EmitterConfig",
    "TransportType",
    "CircuitState",
    "Redactor",
    "RedactionRule",
    "EventSigner",
]
