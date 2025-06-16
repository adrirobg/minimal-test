"""
Keywords endpoints tests
"""
import pytest
from httpx import AsyncClient

from tests.conftest import TestDataFactory


class TestKeywordsEndpoints:
    """Test keywords CRUD endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_keyword(self, client: AsyncClient, auth_headers):
        """Test keyword creation."""
        keyword_data = TestDataFactory.keyword_create_data()
        
        response = await client.post(
            "/api/v1/keywords/", 
            json=keyword_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == keyword_data["name"]
        assert "id" in data
        assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_create_keyword_duplicate(self, client: AsyncClient, auth_headers, test_keyword):
        """Test creating duplicate keyword."""
        keyword_data = {"name": test_keyword.name}
        
        response = await client.post(
            "/api/v1/keywords/", 
            json=keyword_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_keyword_unauthorized(self, client: AsyncClient):
        """Test keyword creation without authentication."""
        keyword_data = TestDataFactory.keyword_create_data()
        
        response = await client.post("/api/v1/keywords/", json=keyword_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_keywords_list(self, client: AsyncClient, auth_headers, test_keyword):
        """Test getting keywords list."""
        response = await client.get("/api/v1/keywords/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        
        # Check if test keyword is in the list
        keyword_ids = [k["id"] for k in data["items"]]
        assert str(test_keyword.id) in keyword_ids
    
    @pytest.mark.asyncio
    async def test_get_keyword_by_id(self, client: AsyncClient, auth_headers, test_keyword):
        """Test getting keyword by ID."""
        response = await client.get(
            f"/api/v1/keywords/{test_keyword.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_keyword.id)
        assert data["name"] == test_keyword.name
        assert "notes_count" in data
        assert "recent_notes" in data
    
    @pytest.mark.asyncio
    async def test_update_keyword(self, client: AsyncClient, auth_headers, test_keyword):
        """Test keyword update."""
        update_data = {"name": "updated-keyword"}
        
        response = await client.put(
            f"/api/v1/keywords/{test_keyword.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    @pytest.mark.asyncio
    async def test_delete_keyword(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test keyword deletion."""
        # Create a keyword to delete
        from app.models.keyword import Keyword
        import uuid
        
        keyword = Keyword(
            id=uuid.uuid4(),
            name="keyword-to-delete",
            user_id=test_user.id
        )
        test_db.add(keyword)
        await test_db.commit()
        await test_db.refresh(keyword)
        
        response = await client.delete(
            f"/api/v1/keywords/{keyword.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_get_keyword_stats(self, client: AsyncClient, auth_headers):
        """Test getting keyword statistics."""
        response = await client.get("/api/v1/keywords/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_create_keywords_bulk(self, client: AsyncClient, auth_headers):
        """Test bulk keyword creation."""
        keyword_names = ["bulk-keyword-1", "bulk-keyword-2", "bulk-keyword-3"]
        
        response = await client.post(
            "/api/v1/keywords/bulk",
            json=keyword_names,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        created_names = [k["name"] for k in data]
        for name in keyword_names:
            assert name in created_names


class TestSourcesEndpoints:
    """Test sources CRUD endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_source(self, client: AsyncClient, auth_headers):
        """Test source creation."""
        source_data = TestDataFactory.source_create_data()
        
        response = await client.post(
            "/api/v1/sources/", 
            json=source_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == source_data["name"]
        assert data["source_type"] == source_data["source_type"]
        assert "id" in data
        assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_create_web_source(self, client: AsyncClient, auth_headers):
        """Test web source creation."""
        source_data = {
            "name": "Test Website",
            "url": "https://example.com"
        }
        
        response = await client.post(
            "/api/v1/sources/web", 
            json=source_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == source_data["name"]
        assert data["source_type"] == "web"
    
    @pytest.mark.asyncio
    async def test_create_book_source(self, client: AsyncClient, auth_headers):
        """Test book source creation."""
        source_data = {
            "name": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890",
            "publication_year": 2023
        }
        
        response = await client.post(
            "/api/v1/sources/book", 
            json=source_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == source_data["name"]
        assert data["source_type"] == "book"
    
    @pytest.mark.asyncio
    async def test_get_sources_list(self, client: AsyncClient, auth_headers, test_source):
        """Test getting sources list."""
        response = await client.get("/api/v1/sources/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_source_by_id(self, client: AsyncClient, auth_headers, test_source):
        """Test getting source by ID."""
        response = await client.get(
            f"/api/v1/sources/{test_source.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_source.id)
        assert data["name"] == test_source.name
        assert "notes_count" in data
        assert "recent_notes" in data
    
    @pytest.mark.asyncio
    async def test_update_source(self, client: AsyncClient, auth_headers, test_source):
        """Test source update."""
        update_data = {
            "name": "Updated Source Name",
            "source_type": "article"
        }
        
        response = await client.put(
            f"/api/v1/sources/{test_source.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["source_type"] == update_data["source_type"]
    
    @pytest.mark.asyncio
    async def test_delete_source(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test source deletion."""
        # Create a source to delete
        from app.models.source import Source
        import uuid
        
        source = Source(
            id=uuid.uuid4(),
            name="Source to Delete",
            source_type="web",
            user_id=test_user.id
        )
        test_db.add(source)
        await test_db.commit()
        await test_db.refresh(source)
        
        response = await client.delete(
            f"/api/v1/sources/{source.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_get_source_types(self, client: AsyncClient):
        """Test getting available source types."""
        response = await client.get("/api/v1/sources/types")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "web" in data
        assert "book" in data
        assert "article" in data
    
    @pytest.mark.asyncio
    async def test_get_source_notes(self, client: AsyncClient, auth_headers, test_source):
        """Test getting notes for a specific source."""
        # Create a note with the source
        note_data = {
            "title": "Note with Source",
            "content": "This note has a source",
            "source_id": str(test_source.id)
        }
        
        await client.post("/api/v1/notes/", json=note_data, headers=auth_headers)
        
        # Get source notes
        response = await client.get(
            f"/api/v1/sources/{test_source.id}/notes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1