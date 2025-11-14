"""
Authentication Module for RAIA Enterprise
==========================================

Provides JWT-based authentication for the RAIA API.

Features:
- JWT token generation and validation
- Password hashing with bcrypt
- User management
- Role-based access control (RBAC)
- API key authentication
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import secrets

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate on first run, store in env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# Models
# ============================================================================

class User(BaseModel):
    """User model."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False
    role: str = "user"  # 'user', 'admin', 'analyst'


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    role: Optional[str] = None


class APIKey(BaseModel):
    """API Key model."""
    key: str
    name: str
    user_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True


# ============================================================================
# Password Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# ============================================================================
# Token Utilities
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload data to encode
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token.

    Args:
        data: Payload data to encode

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token to decode

    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None:
            return None

        return TokenData(username=username, role=role)

    except jwt.PyJWTError:
        return None


# ============================================================================
# User Database (In-Memory for Demo - Use Real DB in Production)
# ============================================================================

# Demo users - In production, store in database
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@raia.com",
        "full_name": "RAIA Administrator",
        "hashed_password": get_password_hash("admin123"),
        "disabled": False,
        "role": "admin"
    },
    "analyst": {
        "username": "analyst",
        "email": "analyst@raia.com",
        "full_name": "RAIA Analyst",
        "hashed_password": get_password_hash("analyst123"),
        "disabled": False,
        "role": "analyst"
    },
    "user": {
        "username": "user",
        "email": "user@raia.com",
        "full_name": "RAIA User",
        "hashed_password": get_password_hash("user123"),
        "disabled": False,
        "role": "user"
    }
}


def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate user with username and password.

    Args:
        username: Username
        password: Plain text password

    Returns:
        User if authenticated, None otherwise
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ============================================================================
# API Key Management
# ============================================================================

# Demo API keys - In production, store in database
fake_api_keys_db = {
    "raia_test_key_123456": {
        "key": "raia_test_key_123456",
        "name": "Test API Key",
        "user_id": "admin",
        "created_at": datetime.utcnow(),
        "expires_at": None,
        "is_active": True
    }
}


def generate_api_key() -> str:
    """Generate a new API key."""
    return f"raia_{secrets.token_urlsafe(32)}"


def create_api_key(name: str, user_id: str, expires_in_days: Optional[int] = None) -> APIKey:
    """
    Create a new API key.

    Args:
        name: Descriptive name for the key
        user_id: User ID who owns the key
        expires_in_days: Optional expiration in days

    Returns:
        Created API key
    """
    key = generate_api_key()
    expires_at = None

    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    api_key = APIKey(
        key=key,
        name=name,
        user_id=user_id,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        is_active=True
    )

    # Store in database (demo uses dict)
    fake_api_keys_db[key] = api_key.dict()

    return api_key


def validate_api_key(api_key: str) -> Optional[str]:
    """
    Validate API key and return user_id.

    Args:
        api_key: API key to validate

    Returns:
        User ID if valid, None otherwise
    """
    key_data = fake_api_keys_db.get(api_key)

    if not key_data:
        return None

    # Check if active
    if not key_data["is_active"]:
        return None

    # Check expiration
    if key_data["expires_at"]:
        expires_at = key_data["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if datetime.utcnow() > expires_at:
            return None

    return key_data["user_id"]


# ============================================================================
# Role-Based Access Control
# ============================================================================

class Permissions:
    """Define permissions for each role."""

    ROLES = {
        "admin": {
            "can_view_all_runs": True,
            "can_delete_runs": True,
            "can_manage_users": True,
            "can_export_data": True,
            "can_view_metrics": True,
        },
        "analyst": {
            "can_view_all_runs": True,
            "can_delete_runs": False,
            "can_manage_users": False,
            "can_export_data": True,
            "can_view_metrics": True,
        },
        "user": {
            "can_view_all_runs": False,
            "can_delete_runs": False,
            "can_manage_users": False,
            "can_export_data": False,
            "can_view_metrics": True,
        }
    }

    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if role has permission."""
        role_perms = Permissions.ROLES.get(role, {})
        return role_perms.get(permission, False)


def require_permission(permission: str):
    """
    Decorator to require specific permission.

    Usage:
        @app.get("/admin/users")
        @require_permission("can_manage_users")
        async def get_users(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        async def wrapper(*args, current_user: User = None, **kwargs):
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")

            if not Permissions.has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {permission}"
                )

            return await func(*args, current_user=current_user, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Database Integration (for production)
# ============================================================================

def init_auth_tables(db_path: str = "raia_auth.db"):
    """
    Initialize authentication tables in database.

    Call this once on first run.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            disabled BOOLEAN DEFAULT 0,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # API Keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Sessions table (for refresh tokens)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            refresh_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

    print(f"✅ Authentication tables initialized in {db_path}")


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    # Initialize database
    init_auth_tables()

    # Create user
    user = authenticate_user("admin", "admin123")
    if user:
        # Create tokens
        access_token = create_access_token({"sub": user.username, "role": user.role})
        refresh_token = create_refresh_token({"sub": user.username})

        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")

        # Decode token
        token_data = decode_token(access_token)
        print(f"Decoded Token: {token_data}")

        # Create API key
        api_key = create_api_key("My API Key", "admin", expires_in_days=30)
        print(f"API Key: {api_key.key}")

        # Validate API key
        user_id = validate_api_key(api_key.key)
        print(f"API Key belongs to user: {user_id}")

        # Check permissions
        can_manage = Permissions.has_permission(user.role, "can_manage_users")
        print(f"Admin can manage users: {can_manage}")
