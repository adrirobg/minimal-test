"""
Test configuration and fixtures
"""
import asyncio
import uuid
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_async_session
from app.core.security import get_password_hash, create_token_response
from app.models.user import User
from app.models.project import Project
from app.models.note import Note
from app.models.keyword import Keyword
from app.models.source import Source


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    TestSessionLocal = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with dependency overrides."""
    
    async def override_get_db():
        yield test_db
    
    from app.api.deps import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=get_password_hash("TestPassword123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(test_db: AsyncSession) -> User:
    """Create a test superuser."""
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash=get_password_hash("AdminPassword123"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(test_user: User) -> str:
    """Create authentication token for test user."""
    token_response = create_token_response(str(test_user.id), test_user.email)
    return token_response["access_token"]


@pytest_asyncio.fixture
async def test_superuser_token(test_superuser: User) -> str:
    """Create authentication token for test superuser."""
    token_response = create_token_response(str(test_superuser.id), test_superuser.email)
    return token_response["access_token"]


@pytest_asyncio.fixture
async def auth_headers(test_user_token: str) -> dict:
    """Create authorization headers for test user."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def admin_headers(test_superuser_token: str) -> dict:
    """Create authorization headers for test superuser."""
    return {"Authorization": f"Bearer {test_superuser_token}"}


@pytest_asyncio.fixture
async def test_project(test_db: AsyncSession, test_user: User) -> Project:
    """Create a test project."""
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="A test project",
        user_id=test_user.id
    )
    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_note(test_db: AsyncSession, test_user: User, test_project: Project) -> Note:
    """Create a test note."""
    note = Note(
        id=uuid.uuid4(),
        title="Test Note",
        content="This is a test note content",
        note_type="text",
        project_id=test_project.id,
        user_id=test_user.id
    )
    test_db.add(note)
    await test_db.commit()
    await test_db.refresh(note)
    return note


@pytest_asyncio.fixture
async def test_keyword(test_db: AsyncSession, test_user: User) -> Keyword:
    """Create a test keyword."""
    keyword = Keyword(
        id=uuid.uuid4(),
        name="test-keyword",
        user_id=test_user.id
    )
    test_db.add(keyword)
    await test_db.commit()
    await test_db.refresh(keyword)
    return keyword


@pytest_asyncio.fixture
async def test_source(test_db: AsyncSession, test_user: User) -> Source:
    """Create a test source."""
    source = Source(
        id=uuid.uuid4(),
        name="Test Source",
        source_type="web",
        source_metadata={"url": "https://example.com"},
        user_id=test_user.id
    )
    test_db.add(source)
    await test_db.commit()
    await test_db.refresh(source)
    return source


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def user_create_data():
        return {
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "full_name": "New User"
        }
    
    @staticmethod
    def project_create_data():
        return {
            "name": "New Project",
            "description": "A new test project"
        }
    
    @staticmethod
    def note_create_data():
        return {
            "title": "New Note",
            "content": "This is a new test note",
            "note_type": "text"
        }
    
    @staticmethod
    def keyword_create_data():
        return {
            "name": "new-keyword"
        }
    
    @staticmethod
    def source_create_data():
        return {
            "name": "New Source",
            "source_type": "article",
            "source_metadata": {"author": "Test Author"}
        }