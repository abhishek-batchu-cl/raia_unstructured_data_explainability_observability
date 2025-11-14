"""
Tests for Authentication Module
================================
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    authenticate_user,
    create_api_key,
    validate_api_key,
    Permissions
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 20

    def test_verify_correct_password(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False


class TestTokenOperations:
    """Test JWT token operations."""

    def test_create_access_token(self):
        """Test access token creation."""
        token = create_access_token({"sub": "testuser", "role": "user"})

        assert isinstance(token, str)
        assert len(token) > 50

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token = create_refresh_token({"sub": "testuser"})

        assert isinstance(token, str)
        assert len(token) > 50

    def test_decode_valid_token(self):
        """Test decoding valid token."""
        token = create_access_token({"sub": "testuser", "role": "admin"})
        token_data = decode_token(token)

        assert token_data is not None
        assert token_data.username == "testuser"
        assert token_data.role == "admin"

    def test_decode_invalid_token(self):
        """Test decoding invalid token."""
        invalid_token = "invalid.token.here"
        token_data = decode_token(invalid_token)

        assert token_data is None

    def test_token_expiration(self):
        """Test token expiration."""
        # Create token with very short expiration
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        token_data = decode_token(token)
        assert token_data is None  # Should fail due to expiration


class TestUserAuthentication:
    """Test user authentication."""

    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials."""
        user = authenticate_user("admin", "admin123")

        assert user is not None
        assert user.username == "admin"
        assert user.role == "admin"

    def test_authenticate_invalid_username(self):
        """Test authentication with invalid username."""
        user = authenticate_user("nonexistent", "password")

        assert user is None

    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        user = authenticate_user("admin", "wrongpassword")

        assert user is None


class TestAPIKeys:
    """Test API key operations."""

    def test_create_api_key(self):
        """Test API key creation."""
        api_key = create_api_key("Test Key", "admin", expires_in_days=30)

        assert api_key.key.startswith("raia_")
        assert api_key.name == "Test Key"
        assert api_key.user_id == "admin"
        assert api_key.is_active is True

    def test_validate_api_key(self):
        """Test API key validation."""
        api_key = create_api_key("Test Key", "admin")
        user_id = validate_api_key(api_key.key)

        assert user_id == "admin"

    def test_validate_invalid_api_key(self):
        """Test validation of invalid API key."""
        user_id = validate_api_key("invalid_key")

        assert user_id is None


class TestPermissions:
    """Test role-based permissions."""

    def test_admin_has_all_permissions(self):
        """Test that admin has all permissions."""
        assert Permissions.has_permission("admin", "can_view_all_runs") is True
        assert Permissions.has_permission("admin", "can_delete_runs") is True
        assert Permissions.has_permission("admin", "can_manage_users") is True
        assert Permissions.has_permission("admin", "can_export_data") is True

    def test_analyst_permissions(self):
        """Test analyst permissions."""
        assert Permissions.has_permission("analyst", "can_view_all_runs") is True
        assert Permissions.has_permission("analyst", "can_export_data") is True
        assert Permissions.has_permission("analyst", "can_delete_runs") is False
        assert Permissions.has_permission("analyst", "can_manage_users") is False

    def test_user_permissions(self):
        """Test user permissions."""
        assert Permissions.has_permission("user", "can_view_metrics") is True
        assert Permissions.has_permission("user", "can_view_all_runs") is False
        assert Permissions.has_permission("user", "can_delete_runs") is False
        assert Permissions.has_permission("user", "can_export_data") is False

    def test_invalid_permission(self):
        """Test invalid permission check."""
        assert Permissions.has_permission("user", "nonexistent_permission") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
