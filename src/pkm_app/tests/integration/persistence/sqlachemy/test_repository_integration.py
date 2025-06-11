import uuid
from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.pkm_app.infrastructure.config.settings import settings
from src.pkm_app.core.application.dtos.keyword_dto import KeywordCreate
from src.pkm_app.core.application.dtos.note_dto import NoteCreate
from src.pkm_app.core.application.dtos.note_link_dto import NoteLinkCreate
from src.pkm_app.core.application.dtos.project_dto import ProjectCreate
from src.pkm_app.core.application.dtos.source_dto import SourceCreate
from src.pkm_app.infrastructure.persistence.sqlalchemy.unit_of_work import SQLAlchemyUnitOfWork
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Base


# Fixtures
@pytest_asyncio.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test function."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def main_db_engine():
    """
    Create an async engine for the real database, creating and dropping tables for the test session.
    """
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Ensure a clean state
        await conn.run_sync(Base.metadata.create_all)  # Create schema

    try:
        yield engine
    finally:
        # Clean up after tests
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session_factory_for_uow(main_db_engine):
    """
    Crea un sessionmaker ligado al engine, para que cada sesión use su propia conexión.
    """
    test_specific_session_factory = sessionmaker(
        bind=main_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    yield test_specific_session_factory


@pytest.fixture(scope="session")
def test_user_id() -> str:
    """Return a test user ID."""
    return "test_user_123"


@pytest_asyncio.fixture(scope="function")
async def uow(async_session_factory_for_uow: sessionmaker):
    """Crea una sesión nueva y un UnitOfWork por test."""
    async with async_session_factory_for_uow() as session:
        uow_instance = SQLAlchemyUnitOfWork(session)
        yield uow_instance


# Tests
@pytest.mark.asyncio
async def test_create_note_with_keywords_and_project(
    uow: SQLAlchemyUnitOfWork,
    test_user_id: str,
):
    """Test creating a note with keywords in a project."""
    async with uow as unit_of_work:
        # Crear un proyecto
        project_data = ProjectCreate(name="Test Project", description="Test Description")
        project = await unit_of_work.projects.create(project_data, test_user_id)

        # Crear una nota con keywords en el proyecto
        note_data = NoteCreate(
            title="Test Note",
            content="Test Content",
            keywords=["test", "integration"],
            project_id=project.id,
        )
        note = await unit_of_work.notes.create(note_data, test_user_id)

        await unit_of_work.commit()

        # Verificar que todo se creó correctamente
        retrieved_note = await unit_of_work.notes.get_by_id(note.id, test_user_id)
        assert retrieved_note is not None
        assert retrieved_note.project_id == project.id
        assert len(retrieved_note.keywords) == 2


@pytest.mark.asyncio
async def test_create_linked_notes_with_source(
    uow: SQLAlchemyUnitOfWork,
    test_user_id: str,
):
    """Test creating linked notes with a source."""
    async with uow as unit_of_work:
        # Crear una fuente
        source_data = SourceCreate(title="Test Source", url="https://example.com", type="article")
        source = await unit_of_work.sources.create(source_data, test_user_id)

        # Crear dos notas relacionadas con la fuente
        note1_data = NoteCreate(title="Note 1", content="Content 1", source_id=source.id)
        note2_data = NoteCreate(title="Note 2", content="Content 2", source_id=source.id)

        note1 = await unit_of_work.notes.create(note1_data, test_user_id)
        note2 = await unit_of_work.notes.create(note2_data, test_user_id)

        # Enlazar las notas
        link_data = NoteLinkCreate(
            source_note_id=note1.id,
            target_note_id=note2.id,
            link_type="reference",
            description="Test link",
        )
        link = await unit_of_work.note_links.create(link_data, test_user_id)

        await unit_of_work.commit()

        # Verificar todo
        note1_retrieved = await unit_of_work.notes.get_by_id(note1.id, test_user_id)
        note2_retrieved = await unit_of_work.notes.get_by_id(note2.id, test_user_id)
        assert note1_retrieved.source_id == source.id
        assert note2_retrieved.source_id == source.id

        # Verificar el enlace
        retrieved_link = await unit_of_work.note_links.get_by_id(link.id, test_user_id)
        assert retrieved_link is not None
        assert retrieved_link.source_note_id == note1.id
        assert retrieved_link.target_note_id == note2.id


@pytest.mark.asyncio
async def test_transaction_rollback_on_error(
    uow: SQLAlchemyUnitOfWork,
    test_user_id: str,
):
    """Test that transactions are rolled back on error."""
    project_id = None
    note_id = None
    keyword_name_for_rollback_test = f"rollback_keyword_{uuid.uuid4()}"

    # Intentar una operación que fallará
    try:
        async with uow as unit_of_work:
            # Crear un proyecto exitosamente
            project = await unit_of_work.projects.create(
                ProjectCreate(name="Test Project for Rollback"), test_user_id
            )
            project_id = project.id

            # Crear una nota exitosamente
            note = await unit_of_work.notes.create(
                NoteCreate(
                    title="Test Note for Rollback", content="Test Content", project_id=project.id
                ),
                test_user_id,
            )
            note_id = note.id

            # Intentar crear un keyword duplicado (debería fallar)
            # The first creation should succeed.
            await unit_of_work.keywords.create(
                KeywordCreate(name=keyword_name_for_rollback_test), test_user_id
            )
            # The second creation with the same name should fail if unique constraints are active.
            await unit_of_work.keywords.create(
                KeywordCreate(name=keyword_name_for_rollback_test), test_user_id
            )

            await unit_of_work.commit()
    except (ValueError, IntegrityError):
        # This block is expected to be hit if the duplicate keyword creation raises an error.
        pass

    # Verificar que nada se guardó debido al rollback
    async with (
        uow as unit_of_work
    ):  # Use a new UoW context for verification if needed, or re-use if appropriate
        project_check = (
            await unit_of_work.projects.get_by_id(project_id, test_user_id) if project_id else None
        )
        note_check = await unit_of_work.notes.get_by_id(note_id, test_user_id) if note_id else None

        # Also, verify the keyword that might have been partially created is not there
        keyword_check = await unit_of_work.keywords.get_by_name(
            keyword_name_for_rollback_test, test_user_id
        )

        assert project_check is None, "Project should have been rolled back"
        assert note_check is None, "Note should have been rolled back"
        assert keyword_check is None, "Keyword should have been rolled back or not committed"


@pytest.mark.asyncio
async def test_complex_project_hierarchy_with_notes(
    uow: SQLAlchemyUnitOfWork,
    test_user_id: str,
):
    """Test creating a complex project hierarchy with notes and links."""
    child_project1_name = "Child Project 1"
    child_project2_name = "Child Project 2"
    async with uow as unit_of_work:
        # Crear una jerarquía de proyectos
        root_project = await unit_of_work.projects.create(
            ProjectCreate(name="Root Project"), test_user_id
        )

        child_project1 = await unit_of_work.projects.create(
            ProjectCreate(name=child_project1_name, parent_project_id=root_project.id), test_user_id
        )

        child_project2 = await unit_of_work.projects.create(
            ProjectCreate(name=child_project2_name, parent_project_id=root_project.id), test_user_id
        )

        # Crear notas en diferentes proyectos
        note1 = await unit_of_work.notes.create(
            NoteCreate(
                title="Note in Root",
                content="Content 1",
                project_id=root_project.id,
                keywords=["root"],
            ),
            test_user_id,
        )

        note2 = await unit_of_work.notes.create(
            NoteCreate(
                title="Note in Child 1",
                content="Content 2",
                project_id=child_project1.id,
                keywords=["child1"],
            ),
            test_user_id,
        )

        note3 = await unit_of_work.notes.create(
            NoteCreate(
                title="Note in Child 2",
                content="Content 3",
                project_id=child_project2.id,
                keywords=["child2"],
            ),
            test_user_id,
        )

        # Crear enlaces entre las notas
        await unit_of_work.note_links.create(
            NoteLinkCreate(
                source_note_id=note1.id, target_note_id=note2.id, link_type="parent-child"
            ),
            test_user_id,
        )

        await unit_of_work.note_links.create(
            NoteLinkCreate(
                source_note_id=note1.id, target_note_id=note3.id, link_type="parent-child"
            ),
            test_user_id,
        )

        await unit_of_work.commit()

        # Verificar la estructura completa
        root = await unit_of_work.projects.get_by_id(root_project.id, test_user_id)
        assert root is not None

        children = await unit_of_work.projects.get_children(root.id, test_user_id)
        assert len(children) == 2

        # Verify children properties (assuming children are returned in a consistent order or checking names)
        child_names_retrieved = sorted([child.name for child in children])
        assert child_names_retrieved == sorted([child_project1_name, child_project2_name])

        # Ensure the specific child projects we created are among the children
        # This also implicitly checks they were correctly parented.
        child_ids_retrieved = [child.id for child in children]
        assert child_project1.id in child_ids_retrieved
        assert child_project2.id in child_ids_retrieved

        # Verificar notas
        root_note = await unit_of_work.notes.get_by_id(note1.id, test_user_id)
        assert root_note is not None
        assert any(k.name == "root" for k in root_note.keywords)

        # Verificar enlaces
        links = await unit_of_work.note_links.get_links_by_source_note(note1.id, test_user_id)
        assert len(links) == 2


@pytest.mark.asyncio
async def test_concurrent_note_creation(
    uow: SQLAlchemyUnitOfWork,
    test_user_id: str,
):
    """Test creating multiple notes concurrently."""
    async with uow as unit_of_work:
        # Crear varias notas en la misma transacción
        notes = []
        for i in range(5):
            note = await unit_of_work.notes.create(
                NoteCreate(title=f"Note {i}", content=f"Content {i}", keywords=[f"keyword{i}"]),
                test_user_id,
            )
            notes.append(note)

        await unit_of_work.commit()

        # Verificar que todas las notas y keywords se crearon
        for note in notes:
            retrieved = await unit_of_work.notes.get_by_id(note.id, test_user_id)
            assert retrieved is not None
            assert len(retrieved.keywords) == 1


@pytest.mark.asyncio
async def test_cascade_delete(
    uow: SQLAlchemyUnitOfWork,
    test_user_id: str,
):
    """Test that deleting a project cascades to notes properly."""
    project_id = None
    note_ids = []

    async with uow as unit_of_work:
        # Crear un proyecto con notas
        project = await unit_of_work.projects.create(
            ProjectCreate(name="Project to Delete"), test_user_id
        )
        project_id = project.id

        # Crear notas en el proyecto
        for i in range(3):
            note = await unit_of_work.notes.create(
                NoteCreate(title=f"Note {i}", content=f"Content {i}", project_id=project.id),
                test_user_id,
            )
            note_ids.append(note.id)

        await unit_of_work.commit()

    # Eliminar el proyecto
    async with uow as unit_of_work:
        await unit_of_work.projects.delete(project_id, test_user_id)
        await unit_of_work.commit()

        # Verificar que las notas también se eliminaron
        for note_id in note_ids:
            note_check = await unit_of_work.notes.get_by_id(note_id, test_user_id)
            assert note_check is None
