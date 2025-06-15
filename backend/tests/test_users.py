"""
Users endpoints tests
"""
import pytest
from httpx import AsyncClient


class TestUsersEndpoints:
    """Test users management endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, client: AsyncClient, auth_headers, test_user):
        """Test getting current user profile."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["id"] == str(test_user.id)
        assert data["is_active"] == test_user.is_active
    
    @pytest.mark.asyncio
    async def test_update_current_user(self, client: AsyncClient, auth_headers, test_user):
        """Test updating current user information."""
        update_data = {
            "full_name": "Updated Full Name",
            "email": "updated@example.com"
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["email"] == update_data["email"]
    
    @pytest.mark.asyncio
    async def test_update_current_user_password(self, client: AsyncClient, auth_headers):
        """Test updating current user password."""
        update_data = {
            "password": "NewPassword123"
        }
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # Password should not be returned
        assert "password" not in response.json()
    
    @pytest.mark.asyncio
    async def test_update_current_user_duplicate_email(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test updating user with duplicate email."""
        # Create another user
        from app.models.user import User
        from app.core.security import get_password_hash
        import uuid
        
        other_user = User(
            id=uuid.uuid4(),
            email="other@example.com",
            password_hash=get_password_hash("Password123"),
            full_name="Other User"
        )
        test_db.add(other_user)
        await test_db.commit()
        
        # Try to update current user with other user's email
        update_data = {"email": "other@example.com"}
        
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_delete_current_user(self, client: AsyncClient, auth_headers):
        """Test deleting current user account."""
        response = await client.delete("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deactivated" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401


class TestAdminUsersEndpoints:
    """Test admin-only user management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_users_as_admin(self, client: AsyncClient, admin_headers, test_user, test_superuser):
        """Test listing users as admin."""
        response = await client.get("/api/v1/users/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 2  # At least test_user and test_superuser
    
    @pytest.mark.asyncio
    async def test_list_users_as_regular_user(self, client: AsyncClient, auth_headers):
        """Test listing users as regular user (should fail)."""
        response = await client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_as_admin(self, client: AsyncClient, admin_headers, test_user):
        """Test getting user by ID as admin."""
        response = await client.get(
            f"/api/v1/users/{test_user.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_as_regular_user(self, client: AsyncClient, auth_headers, test_superuser):
        """Test getting user by ID as regular user (should fail)."""
        response = await client.get(
            f"/api/v1/users/{test_superuser.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_user_as_admin(self, client: AsyncClient, admin_headers, test_user):
        """Test updating user as admin."""
        update_data = {
            "full_name": "Admin Updated Name",
            "is_active": False
        }
        
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["is_active"] == update_data["is_active"]
    
    @pytest.mark.asyncio
    async def test_update_user_as_regular_user(self, client: AsyncClient, auth_headers, test_superuser):
        """Test updating user as regular user (should fail)."""
        update_data = {"full_name": "Hacker Name"}
        
        response = await client.put(
            f"/api/v1/users/{test_superuser.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_delete_user_as_admin(self, client: AsyncClient, admin_headers, test_db, test_superuser):
        """Test deleting user as admin."""
        # Create a user to delete
        from app.models.user import User
        from app.core.security import get_password_hash
        import uuid
        
        user_to_delete = User(
            id=uuid.uuid4(),
            email="deleteme@example.com",
            password_hash=get_password_hash("Password123"),
            full_name="Delete Me"
        )
        test_db.add(user_to_delete)
        await test_db.commit()
        await test_db.refresh(user_to_delete)
        
        response = await client.delete(
            f"/api/v1/users/{user_to_delete.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "deactivated" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_delete_user_as_regular_user(self, client: AsyncClient, auth_headers, test_superuser):
        """Test deleting user as regular user (should fail)."""
        response = await client.delete(
            f"/api/v1/users/{test_superuser.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_users_pagination(self, client: AsyncClient, admin_headers, test_db):
        """Test users list pagination."""
        # Create multiple users
        from app.models.user import User
        from app.core.security import get_password_hash
        import uuid
        
        users = []
        for i in range(3):
            user = User(
                id=uuid.uuid4(),
                email=f"testuser{i}@example.com",
                password_hash=get_password_hash("Password123"),
                full_name=f"Test User {i}"
            )
            users.append(user)
            test_db.add(user)
        
        await test_db.commit()
        
        # Test pagination
        response = await client.get(
            "/api/v1/users/?limit=2&skip=0",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["total"] >= 3
        assert data["limit"] == 2
        assert data["offset"] == 0
    
    @pytest.mark.asyncio
    async def test_users_search(self, client: AsyncClient, admin_headers, test_db):
        """Test users search functionality."""
        # Create a user with specific name
        from app.models.user import User
        from app.core.security import get_password_hash
        import uuid
        
        user = User(
            id=uuid.uuid4(),
            email="searchable@example.com",
            password_hash=get_password_hash("Password123"),
            full_name="Searchable User Name"
        )
        test_db.add(user)
        await test_db.commit()
        
        # Search for the user
        response = await client.get(
            "/api/v1/users/?search=Searchable",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        
        # Check if our user is in results
        found = any(u["full_name"] == "Searchable User Name" for u in data["items"])
        assert found