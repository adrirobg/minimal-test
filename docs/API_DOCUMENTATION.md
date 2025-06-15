# Kairos BCP API Documentation

## Overview

The Kairos BCP Personal Knowledge Management System provides a comprehensive REST API built with FastAPI, featuring JWT authentication, role-based access control, and full CRUD operations for managing notes, projects, sources, and keywords.

**Base URL:** `http://localhost:8000` (development) / `https://api.yourdomain.com` (production)  
**API Version:** v1  
**API Prefix:** `/api/v1`  
**Documentation:** Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Authentication

The API uses **JWT (JSON Web Tokens)** for authentication with Bearer token format.

- **Security Scheme:** HTTP Bearer
- **Token Types:** Access tokens (30 min) + Refresh tokens (7 days)
- **Header Format:** `Authorization: Bearer <access_token>`

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one digit

## Quick Start

1. **Register a new user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

2. **Login to get access token:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

3. **Use the token for authenticated requests:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <your-access-token>"
```

## API Endpoints Reference

### 🔐 Authentication (`/api/v1/auth`)

#### Register New User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### User Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Refresh Access Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

#### Password Reset Request
```http
POST /api/v1/auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

### 👤 User Management (`/api/v1/users`)

#### Get Current User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

#### Update Current User
```http
PUT /api/v1/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "email": "johnsmith@example.com"
}
```

#### List All Users (Admin Only)
```http
GET /api/v1/users?skip=0&limit=20
Authorization: Bearer <admin_access_token>
```

### 📁 Project Management (`/api/v1/projects`)

#### List User Projects
```http
GET /api/v1/projects?skip=0&limit=20
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Research Project",
      "description": "My research notes",
      "user_id": "user-uuid",
      "parent_project_id": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "notes_count": 15,
      "subprojects_count": 2
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### Get Project Tree (Hierarchical)
```http
GET /api/v1/projects/tree
Authorization: Bearer <access_token>
```

#### Create New Project
```http
POST /api/v1/projects
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Research Project",
  "description": "A project for collecting research notes",
  "parent_project_id": null
}
```

#### Get Project by ID
```http
GET /api/v1/projects/{project_id}
Authorization: Bearer <access_token>
```

#### Update Project
```http
PUT /api/v1/projects/{project_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

#### Delete Project
```http
DELETE /api/v1/projects/{project_id}
Authorization: Bearer <access_token>
```

### 📝 Notes Management (`/api/v1/notes`)

#### List User Notes
```http
GET /api/v1/notes?skip=0&limit=20&project_id={project_id}&note_type=text
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Max results (default: 20, max: 100)
- `project_id`: Filter by project UUID
- `note_type`: Filter by note type
- `source_id`: Filter by source UUID

#### Advanced Note Search
```http
GET /api/v1/notes/search?query=research&project_id={uuid}&limit=20
Authorization: Bearer <access_token>
```

**Search Features:**
- Full-text search in title and content
- Filter by project, source, or keywords
- Support for complex search queries

#### Create New Note
```http
POST /api/v1/notes
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Meeting Notes",
  "content": "Important discussion points...",
  "note_type": "text",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "source_id": "550e8400-e29b-41d4-a716-446655440001",
  "keyword_ids": ["keyword1-uuid", "keyword2-uuid"],
  "note_metadata": {
    "tags": ["important", "meeting"],
    "priority": "high"
  }
}
```

**Note Types:** `text`, `markdown`, `task`, `idea`, `reference`, `summary`, `question`

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Meeting Notes",
  "content": "Important discussion points...",
  "note_type": "text",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "source_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "user-uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "project": {...},
  "source": {...},
  "keywords": [...]
}
```

#### Get Note by ID
```http
GET /api/v1/notes/{note_id}
Authorization: Bearer <access_token>
```

#### Update Note
```http
PUT /api/v1/notes/{note_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Meeting Notes",
  "content": "Updated content with more details...",
  "note_type": "text"
}
```

#### Delete Note
```http
DELETE /api/v1/notes/{note_id}
Authorization: Bearer <access_token>
```

### 🏷️ Keywords Management (`/api/v1/keywords`)

#### List User Keywords
```http
GET /api/v1/keywords?skip=0&limit=50
Authorization: Bearer <access_token>
```

#### Get Keyword Usage Statistics
```http
GET /api/v1/keywords/stats?limit=10
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "keyword-uuid",
    "name": "research",
    "usage_count": 25,
    "last_used": "2024-01-01T00:00:00Z"
  }
]
```

#### Create New Keyword
```http
POST /api/v1/keywords
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "machine-learning"
}
```

#### Create Multiple Keywords
```http
POST /api/v1/keywords/bulk
Authorization: Bearer <access_token>
Content-Type: application/json

["research", "machine learning", "ai", "data science"]
```

#### Get Keyword by ID
```http
GET /api/v1/keywords/{keyword_id}
Authorization: Bearer <access_token>
```

#### Update Keyword
```http
PUT /api/v1/keywords/{keyword_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "updated-keyword-name"
}
```

#### Delete Keyword
```http
DELETE /api/v1/keywords/{keyword_id}
Authorization: Bearer <access_token>
```

### 📚 Sources Management (`/api/v1/sources`)

#### List User Sources
```http
GET /api/v1/sources?skip=0&limit=20&source_type=web
Authorization: Bearer <access_token>
```

#### Get Available Source Types
```http
GET /api/v1/sources/types
```

**Response:**
```json
["web", "book", "pdf", "video", "podcast", "article", "paper", "document", "image", "presentation", "other"]
```

#### Create New Source
```http
POST /api/v1/sources
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Important Research Paper",
  "source_type": "paper",
  "source_metadata": {
    "authors": ["Dr. Jane Smith", "Dr. John Doe"],
    "publication": "Nature",
    "year": 2024,
    "doi": "10.1000/journal.issue"
  }
}
```

#### Create Web Source (Specialized)
```http
POST /api/v1/sources/web
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Important Article",
  "source_metadata": {
    "url": "https://example.com/article",
    "title": "Article Title",
    "author": "Author Name",
    "publish_date": "2024-01-01",
    "description": "Article description"
  }
}
```

#### Create Book Source (Specialized)
```http
POST /api/v1/sources/book
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Important Book",
  "source_metadata": {
    "title": "Book Title",
    "authors": ["Author One", "Author Two"],
    "isbn": "978-0123456789",
    "publisher": "Publisher Name",
    "year": 2024,
    "pages": 350
  }
}
```

#### Get Source by ID
```http
GET /api/v1/sources/{source_id}
Authorization: Bearer <access_token>
```

#### Update Source
```http
PUT /api/v1/sources/{source_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Source Name",
  "source_metadata": {
    "updated_field": "new_value"
  }
}
```

#### Delete Source
```http
DELETE /api/v1/sources/{source_id}
Authorization: Bearer <access_token>
```

#### Get Notes for Source
```http
GET /api/v1/sources/{source_id}/notes
Authorization: Bearer <access_token>
```

### 🩺 System Endpoints

#### API Root Information
```http
GET /
```

**Response:**
```json
{
  "message": "Kairos BCP Personal Knowledge Management API",
  "version": "1.0.0",
  "docs_url": "/docs",
  "redoc_url": "/redoc"
}
```

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

## Response Formats

### Standard Response
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 0,
  "has_next": true,
  "has_previous": false
}
```

### Search Response
```json
{
  "results": [...],
  "total": 25,
  "query": "search term",
  "limit": 20,
  "offset": 0
}
```

### Message Response
```json
{
  "message": "Operation completed successfully"
}
```

## Error Handling

### HTTP Status Codes
| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `204` | No Content |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `422` | Unprocessable Entity |
| `429` | Too Many Requests |
| `500` | Internal Server Error |

### Error Response Format
```json
{
  "detail": "Detailed error description",
  "error": "ERROR_CODE",
  "code": "VALIDATION_ERROR",
  "field_errors": {
    "field_name": ["Error message"]
  }
}
```

### Common Error Examples

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Authentication Error (401)
```json
{
  "detail": "Could not validate credentials",
  "error": "INVALID_TOKEN"
}
```

#### Permission Error (403)
```json
{
  "detail": "Not enough permissions",
  "error": "INSUFFICIENT_PERMISSIONS"
}
```

#### Not Found Error (404)
```json
{
  "detail": "Resource not found",
  "error": "NOT_FOUND"
}
```

## Security Features

### Authentication & Authorization
- JWT tokens with configurable expiration (30 min access, 7 days refresh)
- Refresh token rotation for enhanced security
- Password reset functionality with time-limited tokens
- Role-based access control (user/superuser)
- Resource ownership validation

### Data Validation & Security
- Comprehensive Pydantic schemas for all inputs
- SQL injection prevention through SQLAlchemy ORM
- XSS protection via input sanitization
- CORS configuration for cross-origin requests
- Password hashing with bcrypt and salt

### Rate Limiting
- API rate limiting to prevent abuse
- Authentication endpoint throttling
- Configurable rate limits per endpoint

## Performance & Optimization

### Database Performance
- **Async Operations:** All database operations are asynchronous
- **Connection Pooling:** SQLAlchemy async engine with optimized pool settings
- **Query Optimization:** Eager loading for relationships to prevent N+1 queries
- **Indexing:** Strategic database indexes for performance

### API Performance
- **Pagination:** All list endpoints support pagination with configurable limits
- **Search:** Full-text search capabilities with PostgreSQL
- **Caching:** Redis integration for session and data caching
- **Compression:** Response compression for large payloads

### Monitoring
- **Health Checks:** Built-in health check endpoint
- **Logging:** Comprehensive request/response logging
- **Metrics:** Performance metrics collection
- **Error Tracking:** Integration with error tracking services

## SDK & Client Libraries

### Python SDK Example
```python
import httpx

class KairosBCPClient:
    def __init__(self, base_url: str, access_token: str = None):
        self.base_url = base_url
        self.access_token = access_token
        self.client = httpx.AsyncClient()
    
    async def login(self, email: str, password: str):
        response = await self.client.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.access_token = data["access_token"]
        return data
    
    async def create_note(self, title: str, content: str, project_id: str = None):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = await self.client.post(
            f"{self.base_url}/api/v1/notes",
            json={
                "title": title,
                "content": content,
                "note_type": "text",
                "project_id": project_id
            },
            headers=headers
        )
        return response.json()
```

### JavaScript/TypeScript Example
```typescript
class KairosBCPClient {
  private baseUrl: string;
  private accessToken?: string;

  constructor(baseUrl: string, accessToken?: string) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.accessToken = data.access_token;
    return data;
  }

  async createProject(name: string, description?: string) {
    const response = await fetch(`${this.baseUrl}/api/v1/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.accessToken}`
      },
      body: JSON.stringify({ name, description })
    });
    return response.json();
  }
}
```

## Testing

### API Testing with curl
```bash
# Set your access token
export TOKEN="your-access-token"

# Test authentication
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/auth/me

# Create a project
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"Test Project","description":"Test project description"}' \
     http://localhost:8000/api/v1/projects

# Search notes
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/notes/search?query=important&limit=10"
```

### Postman Collection
A Postman collection is available with pre-configured requests for all endpoints. Import the collection from `/docs/postman/kairos-bcp-api.json`.

## Development & Integration

### Interactive Documentation
- **Swagger UI:** Available at `http://localhost:8000/docs`
- **ReDoc:** Available at `http://localhost:8000/redoc`
- **OpenAPI Spec:** Available at `http://localhost:8000/openapi.json`

### Development Setup
1. Clone the repository
2. Set up environment variables (see `.env.example`)
3. Install dependencies: `poetry install`
4. Run database migrations: `alembic upgrade head`
5. Start the server: `uvicorn app.main:app --reload`

### Environment Variables
Key environment variables for API configuration:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `CORS_ORIGINS`: Allowed CORS origins

## Changelog & Versioning

The API follows semantic versioning. Breaking changes will result in a major version increment.

### Current Version: v1.0.0
- Initial release with full CRUD operations
- JWT authentication system
- Role-based access control
- Full-text search capabilities
- Comprehensive error handling

### Roadmap
- [ ] File upload/attachment support
- [ ] Real-time collaboration features
- [ ] Advanced search with filters
- [ ] Bulk operations API
- [ ] Webhook support
- [ ] API rate limiting per user

## Support & Contact

- **Documentation:** http://localhost:8000/docs
- **GitHub Issues:** [Report bugs and feature requests](https://github.com/yourusername/kairos-bcp/issues)
- **Email Support:** support@yourdomain.com

This documentation provides comprehensive coverage of the Kairos BCP API. For additional examples and tutorials, visit the interactive documentation at `/docs`.