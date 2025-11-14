"""
FastAPI Dependencies for RAIA Enterprise
=========================================

Provides reusable dependencies for:
- Authentication (JWT & API Key)
- Authorization (Role-based)
- Database connections
- Rate limiting
- Caching
"""

from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from typing import Optional, Annotated
import sqlite3
from functools import lru_cache

from .auth import decode_token, TokenData, get_user, UserInDB, validate_api_key, Permissions

# ============================================================================
# Authentication Schemes
# ============================================================================

# OAuth2 with Password (and Bearer token)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/token",
    auto_error=False  # Don't auto-error, we'll handle it
)

# API Key Header
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)

# ============================================================================
# Database Dependencies
# ============================================================================

def get_db(db_path: str = "data/demo_databases/complete_end_to_end_demo.db"):
    """
    Get database connection.

    Usage:
        @app.get("/data")
        async def get_data(db = Depends(get_db)):
            cursor = db.cursor()
            ...
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ============================================================================
# Authentication Dependencies
# ============================================================================

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> UserInDB:
    """
    Get current authenticated user from JWT token or API key.

    Supports two authentication methods:
    1. Bearer token (JWT)
    2. X-API-Key header

    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user": user.username}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try JWT token first
    if token:
        token_data = decode_token(token)
        if not token_data or not token_data.username:
            raise credentials_exception

        user = get_user(username=token_data.username)
        if user is None:
            raise credentials_exception

        return user

    # Try API key
    if api_key:
        user_id = validate_api_key(api_key)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key",
            )

        user = get_user(username=user_id)
        if user is None:
            raise credentials_exception

        return user

    # No authentication provided
    raise credentials_exception


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Get current active user (not disabled).

    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_active_user)):
            return {"user": user.username}
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# ============================================================================
# Authorization Dependencies
# ============================================================================

def require_role(allowed_roles: list[str]):
    """
    Require specific role(s).

    Usage:
        @app.get("/admin/users")
        async def get_users(
            user: User = Depends(require_role(["admin"]))
        ):
            ...
    """
    async def role_checker(user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(allowed_roles)}"
            )
        return user

    return role_checker


def require_permission(permission: str):
    """
    Require specific permission.

    Usage:
        @app.delete("/runs/{run_id}")
        async def delete_run(
            run_id: str,
            user: User = Depends(require_permission("can_delete_runs"))
        ):
            ...
    """
    async def permission_checker(user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
        if not Permissions.has_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return user

    return permission_checker


# ============================================================================
# Optional Authentication (for public + protected endpoints)
# ============================================================================

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[UserInDB]:
    """
    Get current user if authenticated, None otherwise.

    Useful for endpoints that work both authenticated and unauthenticated,
    but provide different data based on authentication status.

    Usage:
        @app.get("/data")
        async def get_data(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                # Return full data for authenticated users
                return get_private_data()
            else:
                # Return limited data for public access
                return get_public_data()
    """
    try:
        # Try JWT token
        if token:
            token_data = decode_token(token)
            if token_data and token_data.username:
                user = get_user(username=token_data.username)
                if user and not user.disabled:
                    return user

        # Try API key
        if api_key:
            user_id = validate_api_key(api_key)
            if user_id:
                user = get_user(username=user_id)
                if user and not user.disabled:
                    return user

        return None

    except Exception:
        return None


# ============================================================================
# Rate Limiting Dependencies
# ============================================================================

class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, calls: int = 100, period: int = 60):
        """
        Initialize rate limiter.

        Args:
            calls: Number of calls allowed
            period: Time period in seconds
        """
        self.calls = calls
        self.period = period
        self.requests = {}  # {client_id: [(timestamp, count)]}

    async def __call__(self, request: Request):
        """Check rate limit."""
        import time

        # Get client identifier (IP or user)
        client_id = request.client.host if request.client else "unknown"

        # Clean old requests
        now = time.time()
        if client_id in self.requests:
            self.requests[client_id] = [
                (ts, count) for ts, count in self.requests[client_id]
                if now - ts < self.period
            ]

        # Count requests in current period
        if client_id not in self.requests:
            self.requests[client_id] = []

        request_count = sum(count for _, count in self.requests[client_id])

        if request_count >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.calls} requests per {self.period} seconds."
            )

        # Add current request
        self.requests[client_id].append((now, 1))


# Rate limiter instances
rate_limit_standard = RateLimiter(calls=100, period=60)  # 100 requests per minute
rate_limit_strict = RateLimiter(calls=10, period=60)     # 10 requests per minute


# ============================================================================
# Pagination Dependencies
# ============================================================================

async def pagination_params(
    skip: int = 0,
    limit: int = 100,
    max_limit: int = 1000
):
    """
    Pagination parameters.

    Usage:
        @app.get("/items")
        async def get_items(pagination = Depends(pagination_params)):
            skip, limit = pagination
            ...
    """
    if limit > max_limit:
        limit = max_limit

    if skip < 0:
        skip = 0

    return {"skip": skip, "limit": limit}


# ============================================================================
# Database Query Dependencies
# ============================================================================

class DBQuery:
    """Reusable database query patterns."""

    @staticmethod
    def get_with_auth(
        table: str,
        user: Optional[UserInDB] = None,
        filters: Optional[dict] = None
    ):
        """
        Get data with authentication-based filtering.

        Args:
            table: Table name
            user: Current user (optional)
            filters: Additional filters

        Returns:
            SQL query and parameters
        """
        query = f"SELECT * FROM {table} WHERE 1=1"
        params = []

        # If not admin, filter by user's data
        if user and user.role != "admin":
            query += " AND user_id = ?"
            params.append(user.username)

        # Additional filters
        if filters:
            for key, value in filters.items():
                query += f" AND {key} = ?"
                params.append(value)

        return query, params


# ============================================================================
# Configuration Dependencies
# ============================================================================

@lru_cache()
def get_settings():
    """
    Get application settings (cached).

    Usage:
        @app.get("/config")
        async def get_config(settings = Depends(get_settings)):
            return settings
    """
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        app_name: str = "RAIA Enterprise"
        admin_email: str = "admin@raia.com"
        database_url: str = "sqlite:///data/demo_databases/complete_end_to_end_demo.db"
        redis_url: Optional[str] = None
        postgres_url: Optional[str] = None
        enable_auth: bool = True
        enable_rate_limiting: bool = True
        enable_caching: bool = True
        log_level: str = "INFO"

        class Config:
            env_file = ".env"

    return Settings()


# ============================================================================
# Health Check Dependencies
# ============================================================================

async def check_database_health(db = Depends(get_db)) -> dict:
    """Check database health."""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        return {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


async def check_redis_health() -> dict:
    """Check Redis health."""
    try:
        # Import only if needed
        import redis
        r = redis.from_url("redis://localhost:6379")
        r.ping()
        return {"status": "healthy", "message": "Redis connection OK"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


# ============================================================================
# Export commonly used dependencies
# ============================================================================

# Authentication
CurrentUser = Annotated[UserInDB, Depends(get_current_active_user)]
OptionalUser = Annotated[Optional[UserInDB], Depends(get_current_user_optional)]
AdminUser = Annotated[UserInDB, Depends(require_role(["admin"]))]
AnalystUser = Annotated[UserInDB, Depends(require_role(["admin", "analyst"]))]

# Database
DBConnection = Annotated[sqlite3.Connection, Depends(get_db)]

# Pagination
Pagination = Annotated[dict, Depends(pagination_params)]

# Settings
Settings = Annotated[dict, Depends(get_settings)]
