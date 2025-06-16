"""
Workflow Validation Script
Validates that all user workflows function correctly without errors
"""
import asyncio
import sys
import os
import httpx
import uuid
from typing import Dict, Any, List
import json
import time

# Add backend to path
sys.path.append('/mnt/c/Users/Adri/Proyectos/minimal-test/backend')

from app.core.config import settings

class WorkflowValidator:
    """Validates complete user workflows."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.test_user_email = f"workflow-test-{uuid.uuid4().hex[:8]}@example.com"
        self.test_user_password = "WorkflowTest123"
        self.auth_token = None
        self.created_resources = {
            "users": [],
            "projects": [],
            "notes": [],
            "keywords": [],
            "sources": []
        }
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        await self.client.aclose()
    
    async def cleanup(self):
        """Clean up created test resources."""
        print("🧹 Cleaning up test resources...")
        
        if self.auth_token:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Delete notes
            for note_id in self.created_resources["notes"]:
                try:
                    await self.client.delete(f"/api/v1/notes/{note_id}", headers=headers)
                except:
                    pass
            
            # Delete projects
            for project_id in self.created_resources["projects"]:
                try:
                    await self.client.delete(f"/api/v1/projects/{project_id}", headers=headers)
                except:
                    pass
            
            # Delete keywords
            for keyword_id in self.created_resources["keywords"]:
                try:
                    await self.client.delete(f"/api/v1/keywords/{keyword_id}", headers=headers)
                except:
                    pass
            
            # Delete sources
            for source_id in self.created_resources["sources"]:
                try:
                    await self.client.delete(f"/api/v1/sources/{source_id}", headers=headers)
                except:
                    pass
    
    async def validate_api_health(self) -> bool:
        """Validate API health check."""
        print("🔍 Validating API health...")
        
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ API health check passed")
                    return True
                else:
                    print(f"❌ API health check failed: {data}")
                    return False
            else:
                print(f"❌ API health check failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API health check failed with exception: {e}")
            return False
    
    async def validate_user_registration(self) -> bool:
        """Validate user registration workflow."""
        print("👤 Validating user registration...")
        
        try:
            user_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": "Workflow Test User"
            }
            
            response = await self.client.post("/api/v1/auth/register", json=user_data)
            
            if response.status_code == 201:
                user = response.json()
                self.created_resources["users"].append(user["id"])
                print("✅ User registration successful")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ User registration failed with exception: {e}")
            return False
    
    async def validate_user_authentication(self) -> bool:
        """Validate user authentication workflow."""
        print("🔐 Validating user authentication...")
        
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = await self.client.post("/api/v1/auth/login", json=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                print("✅ User authentication successful")
                return True
            else:
                print(f"❌ User authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ User authentication failed with exception: {e}")
            return False
    
    async def validate_project_crud(self) -> bool:
        """Validate project CRUD operations."""
        print("📁 Validating project CRUD operations...")
        
        if not self.auth_token:
            print("❌ No auth token available for project operations")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Create project
            project_data = {
                "name": "Workflow Test Project",
                "description": "A project created during workflow validation"
            }
            
            response = await self.client.post("/api/v1/projects/", json=project_data, headers=headers)
            
            if response.status_code != 201:
                print(f"❌ Project creation failed: {response.status_code} - {response.text}")
                return False
            
            project = response.json()
            project_id = project["id"]
            self.created_resources["projects"].append(project_id)
            print("✅ Project creation successful")
            
            # Read project
            response = await self.client.get(f"/api/v1/projects/{project_id}", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Project read failed: {response.status_code}")
                return False
            
            print("✅ Project read successful")
            
            # Update project
            update_data = {
                "name": "Updated Workflow Test Project",
                "description": "Updated description"
            }
            
            response = await self.client.put(f"/api/v1/projects/{project_id}", json=update_data, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Project update failed: {response.status_code}")
                return False
            
            print("✅ Project update successful")
            
            # List projects
            response = await self.client.get("/api/v1/projects/", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Project list failed: {response.status_code}")
                return False
            
            projects_response = response.json()
            projects = projects_response.get("items", [])
            if not any(p["id"] == project_id for p in projects):
                print("❌ Created project not found in list")
                return False
            
            print("✅ Project list successful")
            print("✅ All project CRUD operations passed")
            return True
            
        except Exception as e:
            print(f"❌ Project CRUD operations failed with exception: {e}")
            return False
    
    async def validate_note_crud(self) -> bool:
        """Validate note CRUD operations."""
        print("📝 Validating note CRUD operations...")
        
        if not self.auth_token or not self.created_resources["projects"]:
            print("❌ No auth token or project available for note operations")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        project_id = self.created_resources["projects"][0]
        
        try:
            # Create note
            note_data = {
                "title": "Workflow Test Note",
                "content": "This note was created during workflow validation testing",
                "note_type": "text",
                "project_id": project_id
            }
            
            response = await self.client.post("/api/v1/notes/", json=note_data, headers=headers)
            
            if response.status_code != 201:
                print(f"❌ Note creation failed: {response.status_code} - {response.text}")
                return False
            
            note = response.json()
            note_id = note["id"]
            self.created_resources["notes"].append(note_id)
            print("✅ Note creation successful")
            
            # Read note
            response = await self.client.get(f"/api/v1/notes/{note_id}", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Note read failed: {response.status_code}")
                return False
            
            print("✅ Note read successful")
            
            # Update note
            update_data = {
                "title": "Updated Workflow Test Note",
                "content": "Updated content during workflow validation",
                "note_type": "text"
            }
            
            response = await self.client.put(f"/api/v1/notes/{note_id}", json=update_data, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Note update failed: {response.status_code}")
                return False
            
            print("✅ Note update successful")
            
            # List notes
            response = await self.client.get("/api/v1/notes/", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Note list failed: {response.status_code}")
                return False
            
            notes_response = response.json()
            notes = notes_response.get("items", [])
            if not any(n["id"] == note_id for n in notes):
                print("❌ Created note not found in list")
                return False
            
            print("✅ Note list successful")
            
            # Search notes
            response = await self.client.get("/api/v1/notes/search?query=workflow", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Note search failed: {response.status_code}")
                return False
            
            search_response = response.json()
            search_results = search_response.get("results", [])
            if not any(n["id"] == note_id for n in search_results):
                print("❌ Created note not found in search results")
                return False
            
            print("✅ Note search successful")
            print("✅ All note CRUD operations passed")
            return True
            
        except Exception as e:
            print(f"❌ Note CRUD operations failed with exception: {e}")
            return False
    
    async def validate_keyword_crud(self) -> bool:
        """Validate keyword CRUD operations."""
        print("🏷️ Validating keyword CRUD operations...")
        
        if not self.auth_token:
            print("❌ No auth token available for keyword operations")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Create keyword
            keyword_data = {
                "name": "workflow-test-keyword"
            }
            
            response = await self.client.post("/api/v1/keywords/", json=keyword_data, headers=headers)
            
            if response.status_code != 201:
                print(f"❌ Keyword creation failed: {response.status_code} - {response.text}")
                return False
            
            keyword = response.json()
            keyword_id = keyword["id"]
            self.created_resources["keywords"].append(keyword_id)
            print("✅ Keyword creation successful")
            
            # Read keyword
            response = await self.client.get(f"/api/v1/keywords/{keyword_id}", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Keyword read failed: {response.status_code}")
                return False
            
            print("✅ Keyword read successful")
            
            # List keywords
            response = await self.client.get("/api/v1/keywords/", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Keyword list failed: {response.status_code}")
                return False
            
            keywords_response = response.json()
            keywords = keywords_response.get("items", [])
            if not any(k["id"] == keyword_id for k in keywords):
                print("❌ Created keyword not found in list")
                return False
            
            print("✅ Keyword list successful")
            print("✅ All keyword CRUD operations passed")
            return True
            
        except Exception as e:
            print(f"❌ Keyword CRUD operations failed with exception: {e}")
            return False
    
    async def validate_source_crud(self) -> bool:
        """Validate source CRUD operations."""
        print("📚 Validating source CRUD operations...")
        
        if not self.auth_token:
            print("❌ No auth token available for source operations")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Create source
            source_data = {
                "name": "Workflow Test Source",
                "source_type": "web",
                "source_metadata": {"url": "https://example.com/workflow-test"}
            }
            
            response = await self.client.post("/api/v1/sources/", json=source_data, headers=headers)
            
            if response.status_code != 201:
                print(f"❌ Source creation failed: {response.status_code} - {response.text}")
                return False
            
            source = response.json()
            source_id = source["id"]
            self.created_resources["sources"].append(source_id)
            print("✅ Source creation successful")
            
            # Read source
            response = await self.client.get(f"/api/v1/sources/{source_id}", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Source read failed: {response.status_code}")
                return False
            
            print("✅ Source read successful")
            
            # List sources
            response = await self.client.get("/api/v1/sources/", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Source list failed: {response.status_code}")
                return False
            
            sources_response = response.json()
            sources = sources_response.get("items", [])
            if not any(s["id"] == source_id for s in sources):
                print("❌ Created source not found in list")
                return False
            
            print("✅ Source list successful")
            print("✅ All source CRUD operations passed")
            return True
            
        except Exception as e:
            print(f"❌ Source CRUD operations failed with exception: {e}")
            return False
    
    async def validate_complete_workflow(self) -> bool:
        """Validate complete end-to-end workflow."""
        print("🔄 Validating complete end-to-end workflow...")
        
        try:
            # Step 1: Health check
            if not await self.validate_api_health():
                return False
            
            # Step 2: User registration
            if not await self.validate_user_registration():
                return False
            
            # Step 3: User authentication
            if not await self.validate_user_authentication():
                return False
            
            # Step 4: Project management
            if not await self.validate_project_crud():
                return False
            
            # Step 5: Note management
            if not await self.validate_note_crud():
                return False
            
            # Step 6: Keyword management
            if not await self.validate_keyword_crud():
                return False
            
            # Step 7: Source management
            if not await self.validate_source_crud():
                return False
            
            print("🎉 Complete workflow validation successful!")
            return True
            
        except Exception as e:
            print(f"❌ Complete workflow validation failed with exception: {e}")
            return False
    
    async def validate_error_handling(self) -> bool:
        """Validate error handling scenarios."""
        print("⚠️ Validating error handling...")
        
        try:
            # Test 401 unauthorized
            response = await self.client.get("/api/v1/auth/me")
            if response.status_code != 401:
                print(f"❌ Expected 401 for unauthorized request, got {response.status_code}")
                return False
            print("✅ 401 Unauthorized handled correctly")
            
            # Test 404 not found
            fake_id = str(uuid.uuid4())
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(f"/api/v1/projects/{fake_id}", headers=headers)
            if response.status_code != 404:
                print(f"❌ Expected 404 for non-existent resource, got {response.status_code}")
                return False
            print("✅ 404 Not Found handled correctly")
            
            # Test 422 validation error
            invalid_data = {"description": "Missing name field"}
            response = await self.client.post("/api/v1/projects/", json=invalid_data, headers=headers)
            if response.status_code != 422:
                print(f"❌ Expected 422 for validation error, got {response.status_code}")
                return False
            print("✅ 422 Validation Error handled correctly")
            
            print("✅ Error handling validation successful")
            return True
            
        except Exception as e:
            print(f"❌ Error handling validation failed with exception: {e}")
            return False
    
    async def validate_performance_requirements(self) -> bool:
        """Validate basic performance requirements."""
        print("⚡ Validating performance requirements...")
        
        if not self.auth_token:
            print("❌ No auth token available for performance testing")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Test API response times
            start_time = time.time()
            response = await self.client.get("/api/v1/projects/", headers=headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code != 200:
                print(f"❌ Performance test failed: {response.status_code}")
                return False
            
            if response_time > 2.0:  # 2 second threshold
                print(f"❌ API response time too slow: {response_time:.2f}s")
                return False
            
            print(f"✅ API response time acceptable: {response_time:.2f}s")
            
            # Test concurrent requests
            async def make_request():
                return await self.client.get("/api/v1/projects/", headers=headers)
            
            start_time = time.time()
            tasks = [make_request() for _ in range(5)]
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            concurrent_time = end_time - start_time
            
            if any(r.status_code != 200 for r in responses):
                print("❌ Some concurrent requests failed")
                return False
            
            if concurrent_time > 3.0:  # 3 second threshold for 5 concurrent requests
                print(f"❌ Concurrent request time too slow: {concurrent_time:.2f}s")
                return False
            
            print(f"✅ Concurrent request performance acceptable: {concurrent_time:.2f}s")
            print("✅ Performance requirements validation successful")
            return True
            
        except Exception as e:
            print(f"❌ Performance validation failed with exception: {e}")
            return False


async def main():
    """Main validation function."""
    print("🚀 Starting Workflow Validation")
    print("=" * 50)
    
    success = True
    
    async with WorkflowValidator() as validator:
        # Run complete workflow validation
        if not await validator.validate_complete_workflow():
            success = False
        
        print()
        print("=" * 50)
        
        # Run error handling validation
        if not await validator.validate_error_handling():
            success = False
        
        print()
        print("=" * 50)
        
        # Run performance validation
        if not await validator.validate_performance_requirements():
            success = False
    
    print()
    print("=" * 50)
    
    if success:
        print("🎉 ALL WORKFLOW VALIDATIONS PASSED!")
        print("✅ The system is ready for production use")
        return 0
    else:
        print("❌ SOME WORKFLOW VALIDATIONS FAILED!")
        print("⚠️ Please review the errors above before deployment")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())