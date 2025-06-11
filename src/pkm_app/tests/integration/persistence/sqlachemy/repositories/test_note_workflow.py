# tests/integration/persistence/test_note_workflow.py

import pytest
import pytest_asyncio  # For async fixtures
import uuid
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Importaciones de la aplicación
# Ajusta las rutas si es necesario según tu estructura exacta
from src.pkm_app.infrastructure.persistence.sqlalchemy.database import ASYNC_DATABASE_URL
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import (
    Base,
)  # Importa Base para asegurarte de que los modelos están registrados
from src.pkm_app.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SQLAlchemyUnitOfWork,
)
from src.pkm_app.core.application.dtos import (
    NoteCreate,
    NoteSchema,
    UserProfileCreate,
    ProjectCreate,  # Añadido para crear proyectos de prueba
    ProjectSchema,  # Añadido para el fixture de proyecto
)  # Pydantic schemas
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import (
    UserProfile as UserProfileModel,
)  # SQLAlchemy model
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import (
    Note as NoteModel,
)  # Para verificar directamente si es necesario
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import (
    Project as ProjectModel,
)  # Añadido para el fixture de proyecto


# --- Fixtures de Pytest ---


@pytest_asyncio.fixture(scope="session")
async def test_engine_instance():
    """
    Fixture de sesión para crear un motor de base de datos para las pruebas.
    Se conecta a la base de datos definida por ASYNC_DATABASE_URL_STR.
    IMPORTANTE: Este test asume que el esquema de la base de datos ya existe
    (creado por tu seed.sql). No intenta crear/eliminar tablas.
    """
    engine = create_async_engine(
        ASYNC_DATABASE_URL, echo=False
    )  # echo=False para tests más limpios
    yield engine
    await engine.dispose()  # Cierra las conexiones del motor al final de la sesión de tests


@pytest_asyncio.fixture
async def db_transactional_session(test_engine_instance) -> AsyncIterator[AsyncSession]:
    """
    Fixture que proporciona una sesión de base de datos SQLAlchemy AsyncSession.
    Esta sesión está envuelta en una transacción que se revierte después de que el test finaliza,
    asegurando el aislamiento del test y que la base de datos no se modifique permanentemente.
    """
    # Crea una conexión desde el engine
    async with test_engine_instance.connect() as connection:
        # Inicia una transacción en esta conexión
        async with connection.begin() as transaction:
            # Crea una sesión de base de datos usando la conexión y el transaction
            session = sessionmaker(
                bind=connection,
                class_=AsyncSession,
                expire_on_commit=False,  # Para evitar que los objetos se expiren automáticamente al hacer commit
            )()
            try:
                yield session  # Devuelve la sesión para su uso en los tests
            finally:
                await session.close()


@pytest_asyncio.fixture
async def uow(db_transactional_session: AsyncSession) -> SQLAlchemyUnitOfWork:
    """
    Fixture que proporciona una instancia de AsyncSQLAlchemyUnitOfWork.
    Utiliza una fábrica de sesiones que devuelve la sesión transaccional de prueba.
    """
    # Esta fábrica asegura que la UoW use la sesión de prueba gestionada por db_transactional_session
    test_session_factory = lambda: db_transactional_session
    uow_instance = SQLAlchemyUnitOfWork(session_factory=test_session_factory)
    return uow_instance


@pytest_asyncio.fixture
async def test_user(db_transactional_session: AsyncSession) -> UserProfileModel:
    """
    Fixture para crear un usuario de prueba dentro de la transacción del test.
    Devuelve la instancia del modelo SQLAlchemy UserProfile.
    """
    user_id_for_test = f"test_user_notes_{uuid.uuid4()}"
    user_profile = UserProfileModel(
        user_id=user_id_for_test,
        name="Test User for Note Workflow",
        email=f"{user_id_for_test}@example.com",
    )
    db_transactional_session.add(user_profile)
    await db_transactional_session.commit()  # Commit dentro de la transacción del test (se revertirá globalmente)
    await db_transactional_session.refresh(user_profile)
    return user_profile


@pytest_asyncio.fixture
async def test_project(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel) -> ProjectSchema:
    """
    Fixture para crear un proyecto de prueba asociado al test_user.
    Devuelve el ProjectSchema del proyecto creado.
    """
    project_create_data = ProjectCreate(
        name=f"Test Project for Notes {uuid.uuid4()}",
        description="A project to test note associations.",
    )
    async with uow:
        project_schema = await uow.projects.create(
            project_in=project_create_data, user_id=test_user.user_id
        )
        await uow.commit()
    return project_schema


# --- Test Cases ---


@pytest.mark.asyncio
async def test_create_and_retrieve_note_with_uow(
    uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel
):
    """
    Test para crear una nota usando la UoW y el NoteRepository,
    y luego recuperarla para verificar su contenido.
    """
    user_id = test_user.user_id

    note_create_data = NoteCreate(
        title="Nota de Prueba de Integración UoW",
        content="Este es el contenido de la nota de prueba de integración con UoW.",
        type="IntegrationTestNote",
        note_metadata={"priority": 1, "status": "draft"},
        keywords=["integration", "pytest", "uow"],  # Keywords a asociar
    )

    created_note_schema: Optional[NoteSchema] = None
    note_id_created: Optional[uuid.UUID] = None

    # 1. Crear la nota usando la Unidad de Trabajo
    async with uow:  # Entra en el contexto de la UoW (crea sesión, instancia repositorios)
        created_note_schema = await uow.notes.create(note_in=note_create_data, user_id=user_id)
        await uow.commit()  # Confirma la transacción gestionada por la UoW

    # Verificaciones después de la creación
    assert created_note_schema is not None, "La nota creada no debería ser None"
    assert created_note_schema.title == note_create_data.title
    assert created_note_schema.content == note_create_data.content
    assert created_note_schema.user_id == user_id
    assert created_note_schema.id is not None
    note_id_created = created_note_schema.id  # Guardar el ID para la recuperación

    # Verificar keywords (asumiendo que NoteSchema incluye keywords y KeywordSchema tiene 'name')
    assert len(created_note_schema.keywords) == 3
    created_keyword_names = {kw.name for kw in created_note_schema.keywords}
    assert "integration" in created_keyword_names
    assert "pytest" in created_keyword_names
    assert "uow" in created_keyword_names

    # Verificar metadatos
    assert created_note_schema.note_metadata is not None
    assert created_note_schema.note_metadata.get("priority") == 1

    # 2. Recuperar la nota usando la Unidad de Trabajo para verificar la persistencia
    retrieved_note_schema: Optional[NoteSchema] = None
    async with uow:  # Entra en un nuevo contexto de UoW (obtiene una nueva sesión del factory)
        # pero opera dentro de la misma transacción de base de datos gestionada por el fixture
        retrieved_note_schema = await uow.notes.get_by_id(note_id=note_id_created, user_id=user_id)
        # No se necesita commit para operaciones de solo lectura

    # Verificaciones después de la recuperación
    assert retrieved_note_schema is not None, "La nota recuperada no debería ser None"
    assert retrieved_note_schema.id == note_id_created
    assert retrieved_note_schema.title == note_create_data.title
    assert retrieved_note_schema.content == note_create_data.content
    assert retrieved_note_schema.user_id == user_id
    assert retrieved_note_schema.type == note_create_data.type

    # Verificar keywords de la nota recuperada
    assert len(retrieved_note_schema.keywords) == 3
    retrieved_keyword_names = {kw.name for kw in retrieved_note_schema.keywords}
    assert "integration" in retrieved_keyword_names

    # Verificar metadatos de la nota recuperada
    assert retrieved_note_schema.note_metadata is not None
    assert retrieved_note_schema.note_metadata.get("status") == "draft"


@pytest.mark.asyncio
async def test_list_notes_by_user_with_uow(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """
    Test para listar notas de un usuario, verificando paginación básica.
    """
    user_id = test_user.user_id

    # Crear varias notas para el usuario
    async with uow:
        await uow.notes.create(
            note_in=NoteCreate(title="Note List 1", content="Content 1"), user_id=user_id
        )
        await uow.notes.create(
            note_in=NoteCreate(title="Note List 2", content="Content 2"), user_id=user_id
        )
        await uow.notes.create(
            note_in=NoteCreate(title="Note List 3", content="Content 3"), user_id=user_id
        )
        await uow.commit()

    # Listar todas las notas (sin paginación específica más allá del default del repo)
    async with uow:
        notes_page1 = await uow.notes.list_by_user(user_id=user_id, skip=0, limit=2)
        notes_page2 = await uow.notes.list_by_user(user_id=user_id, skip=2, limit=2)
        all_notes = await uow.notes.list_by_user(
            user_id=user_id, limit=10
        )  # Suficientemente grande

    assert len(notes_page1) == 2
    assert notes_page1[0].title == "Note List 3"  # Asumiendo ordenación por updated_at desc
    assert notes_page1[1].title == "Note List 2"

    assert len(notes_page2) == 1
    assert notes_page2[0].title == "Note List 1"

    assert len(all_notes) == 3

    # Probar con un usuario sin notas
    other_user_id = f"other_user_{uuid.uuid4()}"
    async with uow:  # Necesario para que la sesión de uow esté activa
        # Crear el otro usuario si no existe para que la UoW no falle al buscarlo
        # Esto es más un detalle de cómo está implementado el test_user fixture
        # En un caso real, el otro usuario ya existiría o no.
        # Para este test, nos aseguramos que el user_id es válido pero no tiene notas.
        # No es necesario crear el UserProfileModel aquí si el repositorio de notas
        # solo filtra por user_id y no valida su existencia en la tabla de usuarios.
        # Sin embargo, si el repositorio de notas *sí* valida la existencia del user_id,
        # entonces necesitaríamos crear este usuario.
        # Por simplicidad, asumimos que el list_by_user no falla si el user_id es válido
        # pero no tiene notas.
        notes_other_user = await uow.notes.list_by_user(user_id=other_user_id)
    assert len(notes_other_user) == 0


@pytest.mark.asyncio
async def test_update_note_with_uow(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """
    Test para actualizar una nota existente, incluyendo título, contenido y keywords.
    """
    user_id = test_user.user_id

    # 1. Crear una nota inicial
    note_create_data = NoteCreate(
        title="Nota Original para Actualizar",
        content="Contenido original.",
        keywords=["original", "test"],
    )
    async with uow:
        created_note = await uow.notes.create(note_in=note_create_data, user_id=user_id)
        await uow.commit()

    assert created_note is not None
    note_id_to_update = created_note.id
    original_keywords = {kw.name for kw in created_note.keywords}
    assert "original" in original_keywords
    assert "test" in original_keywords
    assert len(original_keywords) == 2

    # 2. Actualizar la nota
    from src.pkm_app.core.application.dtos import NoteUpdate  # Importación local para claridad

    note_update_data = NoteUpdate(
        title="Título Actualizado de Nota",
        content="Contenido actualizado y mejorado.",
        keywords=["actualizado", "test", "nuevo"],  # Cambia keywords
        note_metadata={"status": "finalized", "reviewed": True},
    )

    updated_note_schema: Optional[NoteSchema] = None
    async with uow:
        updated_note_schema = await uow.notes.update(
            note_id=note_id_to_update, note_in=note_update_data, user_id=user_id
        )
        await uow.commit()

    # Verificaciones después de la actualización
    assert updated_note_schema is not None
    assert updated_note_schema.id == note_id_to_update
    assert updated_note_schema.title == "Título Actualizado de Nota"
    assert updated_note_schema.content == "Contenido actualizado y mejorado."
    assert updated_note_schema.user_id == user_id

    # Verificar keywords actualizados
    assert len(updated_note_schema.keywords) == 3
    updated_keyword_names = {kw.name for kw in updated_note_schema.keywords}
    assert "actualizado" in updated_keyword_names
    assert "test" in updated_keyword_names  # 'test' se mantiene
    assert "nuevo" in updated_keyword_names
    assert "original" not in updated_keyword_names  # 'original' se elimina

    # Verificar metadatos actualizados
    assert updated_note_schema.note_metadata is not None
    assert updated_note_schema.note_metadata.get("status") == "finalized"
    assert updated_note_schema.note_metadata.get("reviewed") is True

    # 3. Recuperar y verificar de nuevo para asegurar persistencia de la actualización
    async with uow:
        retrieved_after_update = await uow.notes.get_by_id(
            note_id=note_id_to_update, user_id=user_id
        )

    assert retrieved_after_update is not None
    assert retrieved_after_update.title == "Título Actualizado de Nota"
    retrieved_keywords = {kw.name for kw in retrieved_after_update.keywords}
    assert "actualizado" in retrieved_keywords
    assert "original" not in retrieved_keywords
    assert retrieved_after_update.note_metadata.get("status") == "finalized"


@pytest.mark.asyncio
async def test_delete_note_with_uow(uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel):
    """
    Test para eliminar una nota existente.
    """
    user_id = test_user.user_id

    # 1. Crear una nota para eliminarla
    note_to_delete_data = NoteCreate(title="Nota para Eliminar", content="Contenido a eliminar.")
    async with uow:
        note_to_delete = await uow.notes.create(note_in=note_to_delete_data, user_id=user_id)
        await uow.commit()

    assert note_to_delete is not None
    note_id_to_delete = note_to_delete.id

    # 2. Eliminar la nota
    delete_successful: bool = False
    async with uow:
        delete_successful = await uow.notes.delete(note_id=note_id_to_delete, user_id=user_id)
        await uow.commit()

    assert delete_successful is True

    # 3. Intentar recuperar la nota eliminada (debería ser None)
    async with uow:
        retrieved_deleted_note = await uow.notes.get_by_id(
            note_id=note_id_to_delete, user_id=user_id
        )

    assert retrieved_deleted_note is None

    # 4. Intentar eliminar una nota que no existe (o no pertenece al usuario)
    non_existent_note_id = uuid.uuid4()
    delete_non_existent_successful: bool = True  # Iniciar como True para asegurar que cambia
    async with uow:
        # El método delete del repositorio devuelve False si no se encuentra/elimina
        delete_non_existent_successful = await uow.notes.delete(
            note_id=non_existent_note_id, user_id=user_id
        )
        # No se necesita commit si no hubo cambios, pero por consistencia con el flujo
        # de la UoW, se podría llamar. El repositorio debería manejar esto internamente.
        # await uow.commit() # Opcional aquí, ya que no debería haber cambios.

    assert delete_non_existent_successful is False


@pytest.mark.asyncio
async def test_search_notes_by_project_with_uow(
    uow: SQLAlchemyUnitOfWork, test_user: UserProfileModel, test_project: ProjectSchema
):
    """
    Test para buscar notas asociadas a un proyecto específico.
    """
    user_id = test_user.user_id
    project_id_to_search = test_project.id

    # Crear notas, algunas asociadas al proyecto de prueba y otras no o a otro proyecto
    async with uow:
        # Nota 1 en el proyecto de prueba
        await uow.notes.create(
            note_in=NoteCreate(
                title="Note 1 in Project",
                content="Content for note 1 in project.",
                project_id=project_id_to_search,
            ),
            user_id=user_id,
        )
        # Nota 2 en el proyecto de prueba
        await uow.notes.create(
            note_in=NoteCreate(
                title="Note 2 in Project",
                content="Content for note 2 in project.",
                project_id=project_id_to_search,
                keywords=["project_specific_keyword"],
            ),
            user_id=user_id,
        )
        # Nota 3 sin proyecto
        await uow.notes.create(
            note_in=NoteCreate(
                title="Note without Project", content="Content for note without project."
            ),
            user_id=user_id,
        )
        # Crear otro proyecto para una nota no relacionada (opcional, para mayor robustez)
        other_project_data = ProjectCreate(name=f"Other Project {uuid.uuid4()}")
        other_project = await uow.projects.create(project_in=other_project_data, user_id=user_id)
        await uow.notes.create(
            note_in=NoteCreate(
                title="Note in Other Project",
                content="Content for note in another project.",
                project_id=other_project.id,
            ),
            user_id=user_id,
        )
        await uow.commit()

    # Buscar notas por el project_id_to_search
    async with uow:
        found_notes = await uow.notes.search_by_project(
            project_id=project_id_to_search, user_id=user_id, limit=10
        )

    assert len(found_notes) == 2
    for note in found_notes:
        assert note.project_id == project_id_to_search
        assert note.user_id == user_id

    titles_in_project = {note.title for note in found_notes}
    assert "Note 1 in Project" in titles_in_project
    assert "Note 2 in Project" in titles_in_project

    # Verificar que una búsqueda por un proyecto inexistente (para este usuario) devuelve lista vacía
    non_existent_project_id = uuid.uuid4()
    async with uow:
        notes_non_existent_project = await uow.notes.search_by_project(
            project_id=non_existent_project_id, user_id=user_id
        )
    assert len(notes_non_existent_project) == 0

    # Verificar que la búsqueda en un proyecto sin notas devuelve lista vacía
    project_no_notes_data = ProjectCreate(name=f"Project With No Notes {uuid.uuid4()}")
    async with uow:
        project_no_notes = await uow.projects.create(
            project_in=project_no_notes_data, user_id=user_id
        )
        await uow.commit()
        notes_in_empty_project = await uow.notes.search_by_project(
            project_id=project_no_notes.id, user_id=user_id
        )
    assert len(notes_in_empty_project) == 0
