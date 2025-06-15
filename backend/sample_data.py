#!/usr/bin/env python3
"""
Sample data creation script for Kairos BCP
Creates sample users, projects, notes, and relationships for testing
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.note import Note
from app.models.keyword import Keyword
from app.models.source import Source
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_sample_data():
    """Create sample data for development and testing"""
    async with AsyncSessionLocal() as session:
        try:
            # Create sample user
            logger.info("Creating sample user...")
            sample_user = User(
                email="dev@kairos.local",
                password_hash=get_password_hash("developer123"),
                full_name="Development User",
                is_active=True
            )
            session.add(sample_user)
            await session.flush()  # Get the user ID
            
            # Create sample projects
            logger.info("Creating sample projects...")
            projects = [
                Project(
                    name="Personal Knowledge Base",
                    description="Main repository for personal notes and insights",
                    user_id=sample_user.id
                ),
                Project(
                    name="Learning Resources",
                    description="Collection of learning materials and references",
                    user_id=sample_user.id
                ),
                Project(
                    name="Ideas & Brainstorming",
                    description="Creative ideas and brainstorming sessions",
                    user_id=sample_user.id
                )
            ]
            
            for project in projects:
                session.add(project)
            await session.flush()
            
            # Create sample keywords
            logger.info("Creating sample keywords...")
            keywords = [
                Keyword(
                    name="productivity",
                    user_id=sample_user.id
                ),
                Keyword(
                    name="learning",
                    user_id=sample_user.id
                ),
                Keyword(
                    name="technology",
                    user_id=sample_user.id
                )
            ]
            
            for keyword in keywords:
                session.add(keyword)
            await session.flush()
            
            # Create sample sources
            logger.info("Creating sample sources...")
            sources = [
                Source(
                    name="Getting Things Done",
                    source_type="book",
                    source_metadata={
                        "author": "David Allen",
                        "url": "https://gettingthingsdone.com"
                    },
                    user_id=sample_user.id
                ),
                Source(
                    name="Zettelkasten Method",
                    source_type="article",
                    source_metadata={
                        "author": "Niklas Luhmann",
                        "url": "https://zettelkasten.de"
                    },
                    user_id=sample_user.id
                )
            ]
            
            for source in sources:
                session.add(source)
            await session.flush()
            
            # Create sample notes
            logger.info("Creating sample notes...")
            notes = [
                Note(
                    title="Welcome to Kairos BCP",
                    content="This is your first note in the Kairos BCP system. Use this space to capture your thoughts, ideas, and knowledge.",
                    note_type="note",
                    project_id=projects[0].id,
                    user_id=sample_user.id
                ),
                Note(
                    title="Productivity Systems",
                    content="Key principles of effective productivity systems:\n\n1. Capture everything in a trusted system\n2. Clarify what each item means\n3. Organize by context and priority\n4. Review regularly\n5. Engage with confidence",
                    note_type="note",
                    project_id=projects[0].id,
                    source_id=sources[0].id,
                    user_id=sample_user.id
                ),
                Note(
                    title="Learning Plan 2024",
                    content="## Learning Goals\n\n- Master async Python programming\n- Learn advanced database design\n- Improve system architecture skills\n- Study knowledge management systems",
                    note_type="note",
                    project_id=projects[1].id,
                    user_id=sample_user.id
                ),
                Note(
                    title="PKM System Architecture",
                    content="Ideas for improving the personal knowledge management system:\n\n- Implement graph-based note connections\n- Add semantic search capabilities\n- Create automated tagging\n- Build note templates\n- Integrate with external sources",
                    note_type="idea",
                    project_id=projects[2].id,
                    user_id=sample_user.id
                )
            ]
            
            for note in notes:
                session.add(note)
            
            # Commit all changes
            await session.commit()
            logger.info("Sample data created successfully!")
            
            # Print summary
            logger.info("Sample data summary:")
            logger.info(f"- User: {sample_user.email}")
            logger.info(f"- Projects: {len(projects)}")
            logger.info(f"- Notes: {len(notes)}")
            logger.info(f"- Keywords: {len(keywords)}")
            logger.info(f"- Sources: {len(sources)}")
            
        except Exception as e:
            logger.error(f"Sample data creation failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_sample_data())