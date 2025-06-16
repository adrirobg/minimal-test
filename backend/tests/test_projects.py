"""
Projects endpoints tests
"""
import pytest
from httpx import AsyncClient

from tests.conftest import TestDataFactory


class TestProjectsEndpoints:
    """Test projects CRUD endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_project(self, client: AsyncClient, auth_headers):
        """Test project creation."""
        project_data = TestDataFactory.project_create_data()
        
        response = await client.post(
            "/api/v1/projects/", 
            json=project_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert "id" in data
        assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_create_project_unauthorized(self, client: AsyncClient):
        """Test project creation without authentication."""
        project_data = TestDataFactory.project_create_data()
        
        response = await client.post("/api/v1/projects/", json=project_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_project_invalid_data(self, client: AsyncClient, auth_headers):
        """Test project creation with invalid data."""
        project_data = {"name": ""}  # Empty name
        
        response = await client.post(
            "/api/v1/projects/", 
            json=project_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_projects_list(self, client: AsyncClient, auth_headers, test_project):
        """Test getting projects list."""
        response = await client.get("/api/v1/projects/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        
        # Check if test project is in the list
        project_ids = [p["id"] for p in data["items"]]
        assert str(test_project.id) in project_ids
    
    @pytest.mark.asyncio
    async def test_get_projects_list_unauthorized(self, client: AsyncClient):
        """Test getting projects list without authentication."""
        response = await client.get("/api/v1/projects/")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_project_by_id(self, client: AsyncClient, auth_headers, test_project):
        """Test getting project by ID."""
        response = await client.get(
            f"/api/v1/projects/{test_project.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_project.id)
        assert data["name"] == test_project.name
        assert "notes_count" in data
    
    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client: AsyncClient, auth_headers):
        """Test getting nonexistent project."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = await client.get(
            f"/api/v1/projects/{fake_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_project(self, client: AsyncClient, auth_headers, test_project):
        """Test project update."""
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description"
        }
        
        response = await client.put(
            f"/api/v1/projects/{test_project.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
    
    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client: AsyncClient, auth_headers):
        """Test updating nonexistent project."""
        import uuid
        fake_id = uuid.uuid4()
        update_data = {"name": "Updated Name"}
        
        response = await client.put(
            f"/api/v1/projects/{fake_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_project(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test project deletion."""
        # Create a project to delete
        from app.models.project import Project
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            name="Project to Delete",
            user_id=test_user.id
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)
        
        response = await client.delete(
            f"/api/v1/projects/{project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client: AsyncClient, auth_headers):
        """Test deleting nonexistent project."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = await client.delete(
            f"/api/v1/projects/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_project_tree(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test getting hierarchical project tree."""
        # Create parent and child projects
        from app.models.project import Project
        import uuid
        
        parent_project = Project(
            id=uuid.uuid4(),
            name="Parent Project",
            user_id=test_user.id
        )
        test_db.add(parent_project)
        await test_db.flush()
        
        child_project = Project(
            id=uuid.uuid4(),
            name="Child Project",
            parent_project_id=parent_project.id,
            user_id=test_user.id
        )
        test_db.add(child_project)
        await test_db.commit()
        
        response = await client.get("/api/v1/projects/tree", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Find parent project in tree
        parent_in_tree = None
        for project in data:
            if project["name"] == "Parent Project":
                parent_in_tree = project
                break
        
        assert parent_in_tree is not None
        assert len(parent_in_tree["children"]) >= 1
        assert parent_in_tree["children"][0]["name"] == "Child Project"
    
    @pytest.mark.asyncio
    async def test_create_child_project(self, client: AsyncClient, auth_headers, test_project):
        """Test creating a child project."""
        child_data = {
            "name": "Child Project",
            "description": "A child project",
            "parent_project_id": str(test_project.id)
        }
        
        response = await client.post(
            "/api/v1/projects/",
            json=child_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == child_data["name"]
        assert data["parent_project_id"] == str(test_project.id)
    
    @pytest.mark.asyncio
    async def test_create_child_project_invalid_parent(self, client: AsyncClient, auth_headers):
        """Test creating child project with invalid parent ID."""
        import uuid
        fake_parent_id = uuid.uuid4()
        
        child_data = {
            "name": "Child Project",
            "parent_project_id": str(fake_parent_id)
        }
        
        response = await client.post(
            "/api/v1/projects/",
            json=child_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Parent project not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_projects_pagination(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test projects list pagination."""
        # Create multiple projects
        from app.models.project import Project
        import uuid
        
        projects = []
        for i in range(5):
            project = Project(
                id=uuid.uuid4(),
                name=f"Test Project {i}",
                user_id=test_user.id
            )
            projects.append(project)
            test_db.add(project)
        
        await test_db.commit()
        
        # Test pagination
        response = await client.get(
            "/api/v1/projects/?limit=2&skip=0",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["total"] >= 5
        assert data["limit"] == 2
        assert data["offset"] == 0
    
    @pytest.mark.asyncio
    async def test_projects_search(self, client: AsyncClient, auth_headers, test_db, test_user):
        """Test projects search functionality."""
        # Create a project with specific name
        from app.models.project import Project
        import uuid
        
        project = Project(
            id=uuid.uuid4(),
            name="Searchable Project Name",
            description="This is searchable",
            user_id=test_user.id
        )
        test_db.add(project)
        await test_db.commit()
        
        # Search for the project
        response = await client.get(
            "/api/v1/projects/?search=Searchable",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        
        # Check if our project is in results
        found = any(p["name"] == "Searchable Project Name" for p in data["items"])
        assert found