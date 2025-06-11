# tests/integration/persistence/sqlachemy/repositories/test_project_workflow.py

import pytest
import pytest_asyncio
import uuid
from typing import AsyncIterator, Optional, Dict, Any
import logging
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from aiocache import Cache

from src.pkm_app.core.application.dtos.note_dto import NoteCreate, NoteSchema
from src.pkm_app.core.application.dtos.project_dto import (
    ProjectCreate,
    ProjectSchema,
    ProjectUpdate,
)
from src.pkm_app.infrastructure.persistence.sqlalchemy.database import ASYNC_DATABASE_URL
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import (
    Base,
    UserProfile as UserProfileModel,
)
from src.pkm_app.infrastructure.persistence.sqlalchemy.unit_of_work import SQLAlchemyUnitOfWork


class MockCache:
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.get = AsyncMock()
        self.set = AsyncMock()
        self.delete = AsyncMock()

    async def mock_get(self, key: str) -> Any:
        return self.cache.get(key)

    async def mock_set(self, key: str, value: Any, ttl: int = 0) -> None:
        self.cache[key] = value

    async def mock_delete(self, key: str) -> None:
        self.cache.pop(key, None)


@pytest_asyncio.fixture
def mock_cache() -> MockCache:
    """Fixture que proporciona un mock de Cache para testing."""
    return MockCache()


@pytest_asyncio.fixture
async def engine():
    """Create a test engine instance."""
    test_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncIterator[AsyncSession]:
    """
    Fixture que proporciona una sesión de base de datos SQLAlchemy AsyncSession.
    Esta sesión está envuelta en una transacción que se revierte después del test.
    """
    async_session_factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        async with session.begin():
            yield session


@pytest_asyncio.fixture
async def uow(db_session: AsyncSession, mock_cache: MockCache) -> SQLAlchemyUnitOfWork:
    """
    Fixture que proporciona una instancia de SQLAlchemyUnitOfWork.
    """

    async def _session_factory() -> AsyncSession:
        return db_session

    return SQLAlchemyUnitOfWork(session_factory=_session_factory, cache=mock_cache)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> UserProfileModel:
    """
    Fixture para crear un usuario de prueba dentro de la transacción del test.
    """
    user_id_for_test = f"test_user_projects_{uuid.uuid4()}"
    user_profile = UserProfileModel(
        user_id=user_id_for_test,
        name="Test User for Project Workflow",
        email=f"{user_id_for_test}@example.com",
    )
    db_session.add(user_profile)
    await db_session.flush()
    return user_profile


@pytest.mark.asyncio
async def test_project_cache_operations(
    uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel, mock_cache: MockCache
):
    """Test para verificar el comportamiento del caché en operaciones del repositorio."""
    user_id = test_user.user_id

    # 1. Crear un proyecto
    project_data = ProjectCreate(name="Proyecto Cache Test", description="Test de caché")
    created_project: Optional[ProjectSchema] = None

    async with uow:
        created_project = await uow.projects.create(project_in=project_data, user_id=user_id)
        await uow.commit()

    project_id = created_project.id
    cache_key = f"project_instance:{user_id}:{project_id}:True"

    # 2. Primera lectura (debe guardar en caché)
    async with uow:
        mock_cache.get.reset_mock()
        mock_cache.set.reset_mock()

        project1 = await uow.projects.get_by_id(project_id=project_id, user_id=user_id)

        assert mock_cache.get.called
        assert mock_cache.set.called
        assert project1 is not None
        assert project1.id == project_id

    # 3. Segunda lectura (debe usar caché)
    async with uow:
        mock_cache.get.reset_mock()
        mock_cache.set.reset_mock()

        project2 = await uow.projects.get_by_id(project_id=project_id, user_id=user_id)

        assert mock_cache.get.called
        assert not mock_cache.set.called
        assert project2 is not None
        assert project2.id == project_id

    # 4. Actualizar proyecto (debe invalidar caché)
    update_data = ProjectUpdate(name="Proyecto Cache Test Actualizado")
    async with uow:
        mock_cache.delete.reset_mock()

        updated_project = await uow.projects.update(
            project_id=project_id, project_in=update_data, user_id=user_id
        )
        await uow.commit()

        assert mock_cache.delete.called
        assert updated_project is not None
        assert updated_project.name == update_data.name

    # 5. Verificar que la siguiente lectura no use caché
    async with uow:
        mock_cache.get.reset_mock()
        mock_cache.set.reset_mock()

        project3 = await uow.projects.get_by_id(project_id=project_id, user_id=user_id)

        assert mock_cache.get.called
        assert mock_cache.set.called
        assert project3 is not None
        assert project3.name == update_data.name

    # 6. Eliminar proyecto (debe invalidar caché)
    async with uow:
        mock_cache.delete.reset_mock()

        deleted = await uow.projects.delete(project_id=project_id, user_id=user_id)
        await uow.commit()

        assert mock_cache.delete.called
        assert deleted is True


@pytest.mark.asyncio
async def test_project_logging(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel, caplog):
    """Test para verificar el logging en operaciones del repositorio."""
    caplog.set_level(logging.DEBUG)
    user_id = test_user.user_id

    # 1. Crear un proyecto y verificar logs
    project_data = ProjectCreate(name="Proyecto Log Test", description="Test de logging")
    async with uow:
        created_project = await uow.projects.create(project_in=project_data, user_id=user_id)
        await uow.commit()

        assert any(
            "Intentando crear proyecto" in record.message and user_id in record.message
            for record in caplog.records
        )
        assert any(
            "creado exitosamente" in record.message and user_id in record.message
            for record in caplog.records
        )

    project_id = created_project.id
    caplog.clear()

    # 2. Actualizar proyecto y verificar logs
    update_data = ProjectUpdate(name="Proyecto Log Test Actualizado")
    async with uow:
        updated_project = await uow.projects.update(
            project_id=project_id, project_in=update_data, user_id=user_id
        )
        await uow.commit()

        assert any(
            "Intentando actualizar proyecto" in record.message
            and str(project_id) in record.message
            and user_id in record.message
            for record in caplog.records
        )
        assert any(
            "actualizado exitosamente" in record.message and str(project_id) in record.message
            for record in caplog.records
        )
        assert any(
            "Caché invalidada" in record.message and str(project_id) in record.message
            for record in caplog.records
        )

    caplog.clear()

    # 3. Eliminar proyecto y verificar logs
    async with uow:
        deleted = await uow.projects.delete(project_id=project_id, user_id=user_id)
        await uow.commit()

        assert any(
            "Intentando eliminar proyecto" in record.message
            and str(project_id) in record.message
            and user_id in record.message
            for record in caplog.records
        )
        assert any(
            "eliminado exitosamente" in record.message and str(project_id) in record.message
            for record in caplog.records
        )
        assert any(
            "Caché invalidada" in record.message and str(project_id) in record.message
            for record in caplog.records
        )


@pytest.mark.asyncio
async def test_create_and_retrieve_project(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """Test para crear y recuperar un proyecto usando la UoW."""
    user_id = test_user.user_id

    project_create_data = ProjectCreate(
        name="Proyecto de Test",
        description="Descripción del proyecto de test",
    )

    # 1. Crear el proyecto
    created_project: Optional[ProjectSchema] = None
    async with uow:
        # 1. Crear el proyecto
        created_project = await uow.projects.create(project_in=project_create_data, user_id=user_id)
        await uow.commit()

        # Verificaciones después de la creación
        assert created_project is not None
        assert created_project.name == project_create_data.name
        assert created_project.description == project_create_data.description
        assert created_project.user_id == user_id
        assert created_project.id is not None
        project_id = created_project.id

        # 2. Recuperar el proyecto
        retrieved_project = await uow.projects.get_by_id(project_id=project_id, user_id=user_id)

    # Verificaciones después de la recuperación
    assert retrieved_project is not None
    assert retrieved_project.id == project_id
    assert retrieved_project.name == project_create_data.name
    assert retrieved_project.description == project_create_data.description
    assert retrieved_project.user_id == user_id


@pytest.mark.asyncio
async def test_update_project(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """Test para actualizar un proyecto existente."""
    user_id = test_user.user_id

    # 1. Crear un proyecto inicial
    initial_project = ProjectCreate(name="Proyecto Inicial", description="Descripción inicial")
    created_project: Optional[ProjectSchema] = None
    async with uow:
        created_project = await uow.projects.create(project_in=initial_project, user_id=user_id)
        await uow.commit()
        project_id = created_project.id

    # 2. Actualizar el proyecto
    update_data = ProjectUpdate(name="Proyecto Actualizado", description="Nueva descripción")
    updated_project: Optional[ProjectSchema] = None
    async with uow:
        updated_project = await uow.projects.update(
            project_id=project_id, project_in=update_data, user_id=user_id
        )
        await uow.commit()

    # Verificaciones después de la actualización
    assert updated_project is not None
    assert updated_project.id == project_id
    assert updated_project.name == update_data.name
    assert updated_project.description == update_data.description


@pytest.mark.asyncio
async def test_delete_project_with_notes(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """Test para verificar que al eliminar un proyecto, las notas quedan desasociadas."""
    user_id = test_user.user_id

    # 1. Crear un proyecto
    project_data = ProjectCreate(name="Proyecto a Eliminar", description="Será eliminado")
    created_project: Optional[ProjectSchema] = None
    async with uow:
        created_project = await uow.projects.create(project_in=project_data, user_id=user_id)

    project_id = created_project.id

    # 2. Crear una nota asociada al proyecto
    # Crear nota con proyecto asociado
    note_data = NoteCreate(
        title="Nota Asociada",
        content="Esta nota quedará sin proyecto al eliminar el proyecto",
        type="test",
        project_id=project_id,
    )
    created_note: Optional[NoteSchema] = None
    async with uow:
        created_note = await uow.notes.create(note_in=note_data, user_id=user_id)

    note_id = created_note.id

    # 3. Eliminar el proyecto
    async with uow:
        deleted = await uow.projects.delete(project_id=project_id, user_id=user_id)
        await uow.commit()

    assert deleted is True

    # 4. Verificar que la nota existe pero ya no está asociada al proyecto
    async with uow:
        note_after_delete = await uow.notes.get_by_id(note_id=note_id, user_id=user_id)

    assert note_after_delete is not None
    assert note_after_delete.project_id is None


@pytest.mark.asyncio
async def test_list_projects_by_user(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """Test para listar proyectos de un usuario con paginación."""
    user_id = test_user.user_id

    # 1. Crear varios proyectos
    project_names = ["Proyecto 1", "Proyecto 2", "Proyecto 3"]
    async with uow:
        # Crear proyectos
        for name in project_names:
            await uow.projects.create(
                project_in=ProjectCreate(name=name, description=f"Descripción de {name}"),
                user_id=user_id,
            )
        await uow.commit()

        # Listar y verificar proyectos
        first_page = await uow.projects.list_by_user(user_id=user_id, skip=0, limit=2)
        second_page = await uow.projects.list_by_user(user_id=user_id, skip=2, limit=1)
        all_projects = await uow.projects.list_by_user(user_id=user_id, skip=0, limit=100)

    assert len(first_page) == 2
    assert len(second_page) == 1
    assert len(all_projects) == 3

    # Verificar que los nombres están presentes
    all_names = {p.name for p in all_projects}
    assert all(name in all_names for name in project_names)


@pytest.mark.asyncio
async def test_project_hierarchy(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """Test para verificar la jerarquía de proyectos y get_root_projects."""
    user_id = test_user.user_id

    # 1. Crear proyectos raíz
    async with uow:
        # 1. Crear proyectos raíz
        root1 = await uow.projects.create(project_in=ProjectCreate(name="Root 1"), user_id=user_id)
        root2 = await uow.projects.create(project_in=ProjectCreate(name="Root 2"), user_id=user_id)
        await uow.commit()

        # 2. Crear subproyectos
        child1 = await uow.projects.create(
            project_in=ProjectCreate(name="Child 1", parent_project_id=root1.id), user_id=user_id
        )
        await uow.commit()
        await uow.projects.create(
            project_in=ProjectCreate(name="Child 2", parent_project_id=root1.id), user_id=user_id
        )
        await uow.commit()

    # 3. Verificar get_root_projects
    async with uow:
        root_projects = await uow.projects.get_root_projects(user_id=user_id)

    assert len(root_projects) == 2
    root_names = {p.name for p in root_projects}
    assert "Root 1" in root_names
    assert "Root 2" in root_names

    # 4. Intentar crear una jerarquía circular (debería fallar)
    async with uow:
        with pytest.raises(ValueError):
            await uow.projects.update(
                project_id=root1.id,
                project_in=ProjectUpdate(parent_project_id=child1.id),
                user_id=user_id,
            )


@pytest.mark.asyncio
async def test_user_id_validation(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """Test para verificar que los métodos respetan el user_id."""
    user_id = test_user.user_id
    wrong_user_id = f"wrong_user_{uuid.uuid4()}"

    # 1. Crear un proyecto
    async with uow:
        project = await uow.projects.create(
            project_in=ProjectCreate(name="Proyecto Test"), user_id=user_id
        )
        await uow.commit()
        project_id = project.id

    # 2. Intentar acceder con user_id incorrecto
    async with uow:
        # get_by_id
        retrieved = await uow.projects.get_by_id(project_id=project_id, user_id=wrong_user_id)
        assert retrieved is None

        # update
        updated = await uow.projects.update(
            project_id=project_id,
            project_in=ProjectUpdate(name="Nuevo Nombre"),
            user_id=wrong_user_id,
        )
        assert updated is None

        # delete
        deleted = await uow.projects.delete(project_id=project_id, user_id=wrong_user_id)
        assert deleted is False

        # list_by_user
        wrong_user_projects = await uow.projects.list_by_user(user_id=wrong_user_id)
        assert len(wrong_user_projects) == 0

        # get_root_projects
        wrong_user_roots = await uow.projects.get_root_projects(user_id=wrong_user_id)
        assert len(wrong_user_roots) == 0
