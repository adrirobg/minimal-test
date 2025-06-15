#!/usr/bin/env python3
"""
Debug script to test note creation with keywords
"""
import asyncio
import uuid
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Add the backend path
sys.path.append('/mnt/c/Users/Adri/Proyectos/minimal-test/backend')

from app.core.database import Base
from app.models.user import User
from app.models.note import Note
from app.models.keyword import Keyword
from app.core.security import get_password_hash

async def debug_keyword_association():
    """Test keyword association with notes in SQLite"""
    
    # Create engine
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        try:
            # Create user
            user = User(
                id=uuid.uuid4(),
                email="test@example.com",
                password_hash=get_password_hash("password"),
                full_name="Test User"
            )
            session.add(user)
            await session.flush()
            
            # Create keyword
            keyword = Keyword(
                id=uuid.uuid4(),
                name="test-keyword",
                user_id=user.id
            )
            session.add(keyword)
            await session.flush()
            
            # Create note
            note = Note(
                id=uuid.uuid4(),
                title="Test Note",
                content="Test content",
                user_id=user.id
            )
            session.add(note)
            await session.flush()
            
            # Associate keyword with note
            note.keywords = [keyword]
            
            await session.commit()
            print("✅ Success: Note created with keyword association")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(debug_keyword_association())