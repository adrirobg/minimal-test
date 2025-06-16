"""
Authentication endpoints tests
"""
import pytest
from httpx import AsyncClient

from app.core.security import verify_password, get_password_hash
from tests.conftest import TestDataFactory


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """Test user registration."""
        user_data = TestDataFactory.user_create_data()
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "password" not in data
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,
            "password": "NewPassword123",
            "full_name": "Another User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        user_data = {
            "email": "weak@example.com",
            "password": "123",  # Too short
            "full_name": "Weak Password User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password."""
        login_data = {
            "email": test_user.email,
            "password": "WrongPassword123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers, test_user):
        """Test getting current user info."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["id"] == str(test_user.id)
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user):
        """Test token refresh."""
        # First login to get tokens
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123"
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Use refresh token
        headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
        response = await client.post("/api/v1/auth/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_refresh_token_with_access_token(self, client: AsyncClient, auth_headers):
        """Test refresh endpoint with access token (should fail)."""
        response = await client.post("/api/v1/auth/refresh", headers=auth_headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, auth_headers):
        """Test logout."""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        assert "logged out" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_verify_token(self, client: AsyncClient, auth_headers, test_user):
        """Test token verification."""
        response = await client.post("/api/v1/auth/verify-token", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == str(test_user.id)
    
    @pytest.mark.asyncio
    async def test_password_reset_request(self, client: AsyncClient, test_user):
        """Test password reset request."""
        reset_data = {"email": test_user.email}
        
        response = await client.post("/api/v1/auth/password-reset", json=reset_data)
        
        assert response.status_code == 200
        assert "password reset link" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_password_reset_nonexistent_email(self, client: AsyncClient):
        """Test password reset for nonexistent email."""
        reset_data = {"email": "nonexistent@example.com"}
        
        response = await client.post("/api/v1/auth/password-reset", json=reset_data)
        
        # Should return same message for security
        assert response.status_code == 200
        assert "password reset link" in response.json()["message"]


class TestPasswordSecurity:
    """Test password security functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_password_hash_randomness(self):
        """Test that same password produces different hashes."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)