"""
Audit Logging System for RAIA Enterprise
=========================================

Comprehensive audit logging for:
- Authentication events
- Data access
- Configuration changes
- API calls
- Administrative actions
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
import json
import sqlite3
from contextlib import contextmanager

# ============================================================================
# Models
# ============================================================================

class AuditEventType(str, Enum):
    """Audit event types."""
    # Authentication
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"
    AUTH_PASSWORD_CHANGE = "auth.password_change"

    # Data Access
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"

    # Configuration
    CONFIG_CHANGE = "config.change"
    CONFIG_READ = "config.read"

    # Administrative
    ADMIN_USER_CREATE = "admin.user.create"
    ADMIN_USER_UPDATE = "admin.user.update"
    ADMIN_USER_DELETE = "admin.user.delete"
    ADMIN_ROLE_CHANGE = "admin.role.change"
    ADMIN_PERMISSION_GRANT = "admin.permission.grant"
    ADMIN_PERMISSION_REVOKE = "admin.permission.revoke"

    # System
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"
    SYSTEM_CONFIG_RELOAD = "system.config.reload"

    # API
    API_CALL = "api.call"
    API_RATE_LIMIT = "api.rate_limit"

    # Security
    SECURITY_VIOLATION = "security.violation"
    SECURITY_THREAT_DETECTED = "security.threat_detected"


class AuditSeverity(str, Enum):
    """Audit event severity."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEvent(BaseModel):
    """Audit event model."""
    id: Optional[int] = None
    timestamp: datetime = datetime.utcnow()
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.INFO
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    status: str  # "success", "failure", "error"
    details: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


# ============================================================================
# Audit Logger
# ============================================================================

class AuditLogger:
    """
    Audit logging system with multiple backends.

    Supports:
    - SQLite database storage
    - File-based logging
    - Real-time streaming
    """

    def __init__(self, db_path: str = "audit_logs.db", enable_file: bool = True):
        """
        Initialize audit logger.

        Args:
            db_path: Path to audit database
            enable_file: Enable file-based logging
        """
        self.db_path = db_path
        self.enable_file = enable_file
        self._init_database()

    def _init_database(self):
        """Initialize audit log database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    user_id TEXT,
                    user_role TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indices for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON audit_logs(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id
                ON audit_logs(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type
                ON audit_logs(event_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_severity
                ON audit_logs(severity)
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def log(self, event: AuditEvent) -> int:
        """
        Log audit event.

        Args:
            event: Audit event to log

        Returns:
            Event ID
        """
        # Store in database
        event_id = self._store_in_database(event)

        # Write to file if enabled
        if self.enable_file:
            self._write_to_file(event)

        # Print to console for critical events
        if event.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            print(f"🚨 AUDIT [{event.severity}]: {event.event_type} - {event.action}")

        return event_id

    def _store_in_database(self, event: AuditEvent) -> int:
        """Store event in database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (
                    timestamp, event_type, severity, user_id, user_role,
                    ip_address, user_agent, resource_type, resource_id,
                    action, status, details, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.timestamp.isoformat(),
                event.event_type,
                event.severity,
                event.user_id,
                event.user_role,
                event.ip_address,
                event.user_agent,
                event.resource_type,
                event.resource_id,
                event.action,
                event.status,
                json.dumps(event.details),
                json.dumps(event.metadata)
            ))
            conn.commit()
            return cursor.lastrowid

    def _write_to_file(self, event: AuditEvent):
        """Write event to file."""
        log_file = f"logs/audit_{datetime.utcnow().strftime('%Y-%m-%d')}.log"

        try:
            with open(log_file, 'a') as f:
                log_entry = {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "user_id": event.user_id,
                    "action": event.action,
                    "status": event.status,
                    "details": event.details
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to write audit log to file: {e}")

    def query(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEvent]:
        """
        Query audit logs.

        Args:
            start_time: Start time filter
            end_time: End time filter
            user_id: User ID filter
            event_type: Event type filter
            severity: Severity filter
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of audit events
        """
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            events = []
            for row in rows:
                event = AuditEvent(
                    id=row['id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    event_type=row['event_type'],
                    severity=row['severity'],
                    user_id=row['user_id'],
                    user_role=row['user_role'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    resource_type=row['resource_type'],
                    resource_id=row['resource_id'],
                    action=row['action'],
                    status=row['status'],
                    details=json.loads(row['details']) if row['details'] else {},
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                events.append(event)

            return events

    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get audit statistics.

        Args:
            hours: Hours to look back

        Returns:
            Statistics dictionary
        """
        start_time = datetime.utcnow().timestamp() - (hours * 3600)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total events
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM audit_logs
                WHERE timestamp >= datetime(?, 'unixepoch')
            """, (start_time,))
            total = cursor.fetchone()['total']

            # Events by type
            cursor.execute("""
                SELECT event_type, COUNT(*) as count
                FROM audit_logs
                WHERE timestamp >= datetime(?, 'unixepoch')
                GROUP BY event_type
                ORDER BY count DESC
            """, (start_time,))
            by_type = {row['event_type']: row['count'] for row in cursor.fetchall()}

            # Events by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM audit_logs
                WHERE timestamp >= datetime(?, 'unixepoch')
                GROUP BY severity
            """, (start_time,))
            by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}

            # Top users
            cursor.execute("""
                SELECT user_id, COUNT(*) as count
                FROM audit_logs
                WHERE timestamp >= datetime(?, 'unixepoch')
                AND user_id IS NOT NULL
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
            """, (start_time,))
            top_users = {row['user_id']: row['count'] for row in cursor.fetchall()}

            # Failed events
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM audit_logs
                WHERE timestamp >= datetime(?, 'unixepoch')
                AND status = 'failure'
            """, (start_time,))
            failed = cursor.fetchone()['count']

            return {
                "total_events": total,
                "events_by_type": by_type,
                "events_by_severity": by_severity,
                "top_users": top_users,
                "failed_events": failed,
                "time_range_hours": hours
            }


# ============================================================================
# Audit Decorators
# ============================================================================

def audit_action(
    event_type: AuditEventType,
    action: str,
    resource_type: Optional[str] = None
):
    """
    Decorator to audit function calls.

    Usage:
        @audit_action(AuditEventType.DATA_READ, "Get user data", "users")
        def get_user(user_id: str, current_user: User):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            from functools import wraps

            @wraps(func)
            async def inner(*args, **kwargs):
                # Get current user from kwargs
                current_user = kwargs.get('current_user') or kwargs.get('user')
                resource_id = kwargs.get('id') or kwargs.get('run_id')

                # Execute function
                try:
                    result = await func(*args, **kwargs)
                    status = "success"
                    details = {}
                except Exception as e:
                    status = "failure"
                    details = {"error": str(e)}
                    raise
                finally:
                    # Log audit event
                    event = AuditEvent(
                        event_type=event_type,
                        severity=AuditSeverity.INFO if status == "success" else AuditSeverity.ERROR,
                        user_id=current_user.username if current_user else None,
                        user_role=current_user.role if current_user else None,
                        resource_type=resource_type,
                        resource_id=str(resource_id) if resource_id else None,
                        action=action,
                        status=status,
                        details=details
                    )
                    # Assume global audit_logger instance
                    # audit_logger.log(event)

                return result

            return await inner(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Global Audit Logger Instance
# ============================================================================

# Initialize global logger
audit_logger = AuditLogger()


# ============================================================================
# Helper Functions
# ============================================================================

def log_authentication(
    user_id: str,
    success: bool,
    ip_address: Optional[str] = None,
    details: Optional[Dict] = None
):
    """Log authentication event."""
    event = AuditEvent(
        event_type=AuditEventType.AUTH_LOGIN if success else AuditEventType.AUTH_FAILED,
        severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
        user_id=user_id,
        ip_address=ip_address,
        action="User authentication",
        status="success" if success else "failure",
        details=details or {}
    )
    audit_logger.log(event)


def log_data_access(
    user_id: str,
    user_role: str,
    resource_type: str,
    resource_id: str,
    action: str,
    success: bool = True
):
    """Log data access event."""
    event = AuditEvent(
        event_type=AuditEventType.DATA_READ,
        user_id=user_id,
        user_role=user_role,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        status="success" if success else "failure"
    )
    audit_logger.log(event)


def log_admin_action(
    admin_id: str,
    action: str,
    target_user: Optional[str] = None,
    details: Optional[Dict] = None
):
    """Log administrative action."""
    event = AuditEvent(
        event_type=AuditEventType.ADMIN_USER_UPDATE,
        severity=AuditSeverity.WARNING,
        user_id=admin_id,
        action=action,
        status="success",
        details=details or {},
        metadata={"target_user": target_user} if target_user else {}
    )
    audit_logger.log(event)


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    # Initialize logger
    logger = AuditLogger()

    # Log authentication
    log_authentication(
        user_id="admin",
        success=True,
        ip_address="192.168.1.100",
        details={"method": "jwt"}
    )

    # Log data access
    log_data_access(
        user_id="analyst",
        user_role="analyst",
        resource_type="runs",
        resource_id="run_123",
        action="View run details"
    )

    # Log admin action
    log_admin_action(
        admin_id="admin",
        action="Updated user role",
        target_user="user123",
        details={"old_role": "user", "new_role": "analyst"}
    )

    # Query logs
    events = logger.query(user_id="admin", limit=10)
    print(f"\nFound {len(events)} events for user 'admin'")
    for event in events:
        print(f"  - {event.timestamp}: {event.event_type} - {event.action}")

    # Get statistics
    stats = logger.get_stats(hours=24)
    print(f"\nAudit Statistics (last 24 hours):")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Failed events: {stats['failed_events']}")
    print(f"  Events by type: {stats['events_by_type']}")
