"""
Notes endpoints tests
"""
import pytest
from httpx import AsyncClient

from tests.conftest import TestDataFactory


class TestNotesEndpoints:
    """Test notes CRUD endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_note(self, client: AsyncClient, auth_headers):
        """Test note creation."""
        note_data = TestDataFactory.note_create_data()
        
        response = await client.post(
            "/api/v1/notes/", 
            json=note_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == note_data["title"]
        assert data["content"] == note_data["content"]
        assert data["note_type"] == note_data["note_type"]
        assert "id" in data
        assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_create_note_with_project(self, client: AsyncClient, auth_headers, test_project):
        """Test note creation with project assignment."""
        note_data = {
            **TestDataFactory.note_create_data(),
            "project_id": str(test_project.id)
        }
        
        response = await client.post(
            "/api/v1/notes/", 
            json=note_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == str(test_project.id)
    
    @pytest.mark.asyncio
    async def test_create_note_with_source(self, client: AsyncClient, auth_headers, test_source):
        """Test note creation with source assignment."""
        note_data = {
            **TestDataFactory.note_create_data(),
            "source_id": str(test_source.id)
        }
        
        response = await client.post(
            "/api/v1/notes/", 
            json=note_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["source_id"] == str(test_source.id)
    
    @pytest.mark.asyncio
    async def test_create_note_with_keywords(self, client: AsyncClient, auth_headers, test_keyword):
        """Test note creation with keyword assignment."""
        note_data = {
            **TestDataFactory.note_create_data(),
            "keyword_ids": [str(test_keyword.id)]
        }
        
        response = await client.post(
            "/api/v1/notes/", 
            json=note_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_note_unauthorized(self, client: AsyncClient):
        """Test note creation without authentication."""
        note_data = TestDataFactory.note_create_data()
        
        response = await client.post("/api/v1/notes/", json=note_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_note_invalid_data(self, client: AsyncClient, auth_headers):
        """Test note creation with invalid data."""
        note_data = {"content": ""}  # Empty content
        
        response = await client.post(
            "/api/v1/notes/", 
            json=note_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_notes_list(self, client: AsyncClient, auth_headers, test_note):
        """Test getting notes list."""
        response = await client.get("/api/v1/notes/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        
        # Check if test note is in the list
        note_ids = [n["id"] for n in data["items"]]
        assert str(test_note.id) in note_ids
    
    @pytest.mark.asyncio
    async def test_get_notes_list_unauthorized(self, client: AsyncClient):
        """Test getting notes list without authentication."""
        response = await client.get("/api/v1/notes/")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_note_by_id(self, client: AsyncClient, auth_headers, test_note):
        """Test getting note by ID."""
        response = await client.get(
            f"/api/v1/notes/{test_note.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_note.id)
        assert data["title"] == test_note.title
        assert data["content"] == test_note.content
        assert "keywords" in data
        assert "outgoing_links_count" in data
        assert "incoming_links_count" in data
    
    @pytest.mark.asyncio
    async def test_get_note_not_found(self, client: AsyncClient, auth_headers):
        """Test getting nonexistent note."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = await client.get(
            f"/api/v1/notes/{fake_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_note(self, client: AsyncClient, auth_headers, test_note):
        """Test note update."""
        update_data = {
            "title": "Updated Note Title",
            "content": "Updated note content",
            "note_type": "markdown"
        }
        
        response = await client.put(
            f"/api/v1/notes/{test_note.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
        assert data["note_type"] == update_data["note_type"]
    
    @pytest.mark.asyncio
    async def test_update_note_not_found(self, client: AsyncClient, auth_headers):
        """Test updating nonexistent note."""
        import uuid
        fake_id = uuid.uuid4()
        update_data = {"title": "Updated Title"}
        
        response = await client.put(
            f"/api/v1/notes/{fake_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_note(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test note deletion."""
        # Create a note to delete
        from app.models.note import Note
        import uuid
        
        note = Note(
            id=uuid.uuid4(),
            title="Note to Delete",
            content="This note will be deleted",
            user_id=test_user.id
        )
        test_db.add(note)
        await test_db.commit()
        await test_db.refresh(note)
        
        response = await client.delete(
            f"/api/v1/notes/{note.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_delete_note_not_found(self, client: AsyncClient, auth_headers):
        """Test deleting nonexistent note."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = await client.delete(
            f"/api/v1/notes/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_search_notes(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test notes search functionality."""
        # Create a note with specific content
        from app.models.note import Note
        import uuid
        
        note = Note(
            id=uuid.uuid4(),
            title="Searchable Note",
            content="This note contains searchable content about Python programming",
            note_type="text",
            user_id=test_user.id
        )
        test_db.add(note)
        await test_db.commit()
        
        # Search for the note
        response = await client.get(
            "/api/v1/notes/search?query=Python",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert len(data["results"]) >= 1
        
        # Check if our note is in results
        found = any(n["title"] == "Searchable Note" for n in data["results"])
        assert found
    
    @pytest.mark.asyncio
    async def test_search_notes_with_filters(self, client: AsyncClient, auth_headers, test_note, test_project):
        """Test notes search with project filter."""
        response = await client.get(
            f"/api/v1/notes/search?query=test&project_id={test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
    
    @pytest.mark.asyncio
    async def test_notes_pagination(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test notes list pagination."""
        # Create multiple notes
        from app.models.note import Note
        import uuid
        
        notes = []
        for i in range(5):
            note = Note(
                id=uuid.uuid4(),
                title=f"Test Note {i}",
                content=f"Content for note {i}",
                user_id=test_user.id
            )
            notes.append(note)
            test_db.add(note)
        
        await test_db.commit()
        
        # Test pagination
        response = await client.get(
            "/api/v1/notes/?limit=2&skip=0",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["total"] >= 5
        assert data["limit"] == 2
        assert data["offset"] == 0
    
    @pytest.mark.asyncio
    async def test_notes_filter_by_project(self, client: AsyncClient, auth_headers, test_note, test_project):
        """Test filtering notes by project."""
        response = await client.get(
            f"/api/v1/notes/?project_id={test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        # All returned notes should belong to the project
        for note in data["items"]:
            if note["project_id"]:
                assert note["project_id"] == str(test_project.id)
    
    @pytest.mark.asyncio
    async def test_notes_filter_by_source(self, client: AsyncClient, auth_headers, test_source):
        """Test filtering notes by source."""
        # Create a note with the source
        note_data = {
            **TestDataFactory.note_create_data(),
            "source_id": str(test_source.id)
        }
        
        create_response = await client.post(
            "/api/v1/notes/", 
            json=note_data, 
            headers=auth_headers
        )
        assert create_response.status_code == 201
        
        # Filter by source
        response = await client.get(
            f"/api/v1/notes/?source_id={test_source.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        
        # All returned notes should belong to the source
        for note in data["items"]:
            if note["source_id"]:
                assert note["source_id"] == str(test_source.id)
    
    @pytest.mark.asyncio
    async def test_notes_filter_by_type(self, client: AsyncClient, auth_headers):
        """Test filtering notes by type."""
        # Create notes with different types
        note_data_text = {
            **TestDataFactory.note_create_data(),
            "note_type": "text"
        }
        note_data_markdown = {
            **TestDataFactory.note_create_data(),
            "note_type": "markdown",
            "title": "Markdown Note"
        }
        
        await client.post("/api/v1/notes/", json=note_data_text, headers=auth_headers)
        await client.post("/api/v1/notes/", json=note_data_markdown, headers=auth_headers)
        
        # Filter by type
        response = await client.get(
            "/api/v1/notes/?note_type=markdown",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned notes should be markdown type
        for note in data["items"]:
            assert note["note_type"] == "markdown"