import uuid
from collections.abc import Sequence
from typing import Optional

from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import or_, select, true
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

# Esquemas Pydantic
from src.pkm_app.core.application.dtos import NoteCreate, NoteSchema, NoteUpdate

# Interfaz del Repositorio
from src.pkm_app.core.application.interfaces.note_interface import INoteRepository
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Keyword as KeywordModel

# Modelos SQLAlchemy
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Note as NoteModel
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Project as ProjectModel
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Source as SourceModel
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import UserProfile as UserProfileModel


class SQLAlchemyNoteRepository(INoteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_note_instance(self, note_id: uuid.UUID, user_id: str) -> NoteModel | None:
        """Método helper para obtener una instancia de NoteModel."""
        stmt = (
            select(NoteModel)
            .where(NoteModel.id == note_id, NoteModel.user_id == user_id)
            .options(
                selectinload(NoteModel.keywords),  # Carga ansiosa de keywords
                joinedload(NoteModel.project),  # Carga ansiosa del proyecto (si existe)
                joinedload(NoteModel.source),  # Carga ansiosa de la fuente (si existe)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _manage_keywords(
        self, note_instance: NoteModel, keyword_names: list[str] | None, user_id: str
    ) -> None:
        """Método helper para gestionar los keywords de una nota."""
        if keyword_names is None:  # Si es None, no se hace nada con los keywords
            return

        # Eliminar keywords actuales de la nota para luego añadir los nuevos
        note_instance.keywords.clear()

        if not keyword_names:  # Si la lista está vacía, se eliminan todos los keywords
            return

        final_keywords: list[KeywordModel] = []
        for name in set(keyword_names):  # Usar set para evitar duplicados en la entrada
            if not name.strip():  # Omitir keywords vacíos
                continue

            # Buscar si el keyword ya existe para este usuario
            stmt_keyword = select(KeywordModel).where(
                KeywordModel.user_id == user_id, KeywordModel.name == name
            )
            result_keyword = await self.session.execute(stmt_keyword)
            keyword_instance = result_keyword.scalar_one_or_none()

            if not keyword_instance:
                # Crear keyword si no existe
                keyword_instance = KeywordModel(user_id=user_id, name=name)
                self.session.add(keyword_instance)
            final_keywords.append(keyword_instance)

        note_instance.keywords.extend(final_keywords)

    async def get_by_id(self, note_id: uuid.UUID, user_id: str) -> NoteSchema | None:
        note_instance = await self._get_note_instance(note_id, user_id)
        if note_instance:
            return NoteSchema.model_validate(note_instance)
        return None

    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> list[NoteSchema]:
        stmt = (
            select(NoteModel)
            .where(NoteModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(NoteModel.updated_at.desc())  # Ejemplo de ordenación
            .options(
                selectinload(NoteModel.keywords),  # Carga ansiosa de keywords
                joinedload(NoteModel.project),  # Carga ansiosa del proyecto (si existe)
                # joinedload(NoteModel.source)    # Decidir si cargar source aquí o bajo demanda
            )
        )
        result = await self.session.execute(stmt)
        notes_orm = result.scalars().all()
        return [NoteSchema.model_validate(note) for note in notes_orm]

    async def create(self, note_in: NoteCreate, user_id: str) -> NoteSchema:
        # Validar existencia de project_id y source_id si se proporcionan
        if note_in.project_id:
            project_stmt = select(ProjectModel.id).where(
                ProjectModel.id == note_in.project_id, ProjectModel.user_id == user_id
            )
            project_exists = await self.session.execute(project_stmt)
            if not project_exists.scalar_one_or_none():
                raise ValueError(
                    f"Proyecto con id {note_in.project_id} no encontrado para el usuario."
                )

        if note_in.source_id:
            source_stmt = select(SourceModel.id).where(
                SourceModel.id == note_in.source_id, SourceModel.user_id == user_id
            )
            source_exists = await self.session.execute(source_stmt)
            if not source_exists.scalar_one_or_none():
                raise ValueError(
                    f"Fuente con id {note_in.source_id} no encontrada para el usuario."
                )

        # Crear la instancia del modelo NoteModel
        db_note_data = note_in.model_dump(
            exclude_unset=True, exclude={"keywords"}
        )  # Excluir keywords del dump inicial

        note_instance = NoteModel(**db_note_data, user_id=user_id)

        # Gestionar keywords
        await self._manage_keywords(note_instance, note_in.keywords, user_id)

        self.session.add(note_instance)
        await self.session.flush()  # Para obtener el ID y otros defaults de la BD antes de refresh
        await self.session.refresh(
            note_instance, attribute_names=["id", "created_at", "updated_at"]
        )  # Refrescar solo campos necesarios
        await self.session.refresh(
            note_instance, attribute_names=["keywords", "project", "source"]
        )  # Refrescar relaciones

        return NoteSchema.model_validate(note_instance)

    async def update(
        self, note_id: uuid.UUID, note_in: NoteUpdate, user_id: str
    ) -> NoteSchema | None:
        note_instance = await self._get_note_instance(note_id, user_id)
        if not note_instance:
            return None

        update_data = note_in.model_dump(exclude_unset=True, exclude={"keywords"})
        for field, value in update_data.items():
            # Validar project_id y source_id si se están actualizando
            if field == "project_id" and value is not None:
                project_stmt = select(ProjectModel.id).where(
                    ProjectModel.id == value, ProjectModel.user_id == user_id
                )
                project_exists = await self.session.execute(project_stmt)
                if not project_exists.scalar_one_or_none():
                    raise ValueError(f"Proyecto con id {value} no encontrado para el usuario.")
            elif field == "source_id" and value is not None:
                source_stmt = select(SourceModel.id).where(
                    SourceModel.id == value, SourceModel.user_id == user_id
                )
                source_exists = await self.session.execute(source_stmt)
                if not source_exists.scalar_one_or_none():
                    raise ValueError(f"Fuente con id {value} no encontrada para el usuario.")
            setattr(note_instance, field, value)

        # Gestionar keywords si se proporcionan en la actualización
        if note_in.keywords is not None:  # Chequeo explícito de None para permitir lista vacía
            await self._manage_keywords(note_instance, note_in.keywords, user_id)

        self.session.add(note_instance)  # SQLAlchemy rastrea los cambios
        await self.session.flush()
        await self.session.refresh(
            note_instance, attribute_names=["updated_at"]
        )  # Refrescar campos afectados
        await self.session.refresh(
            note_instance, attribute_names=["keywords", "project", "source"]
        )  # Refrescar relaciones

        return NoteSchema.model_validate(note_instance)

    async def delete(self, note_id: uuid.UUID, user_id: str) -> bool:
        note_instance = await self._get_note_instance(note_id, user_id)
        if note_instance:
            await self.session.delete(note_instance)
            await self.session.flush()
            return True
        return False

    async def search_by_title_or_content(
        self, user_id: str, query: str, skip: int = 0, limit: int = 20
    ) -> list[NoteSchema]:
        search_term = f"%{query}%"
        stmt = (
            select(NoteModel)
            .where(
                NoteModel.user_id == user_id,
                or_(
                    NoteModel.title.ilike(search_term),  # Búsqueda case-insensitive
                    NoteModel.content.ilike(search_term),
                ),
            )
            .offset(skip)
            .limit(limit)
            .order_by(NoteModel.updated_at.desc())
            .options(selectinload(NoteModel.keywords))  # Cargar keywords
        )
        result = await self.session.execute(stmt)
        notes_orm = result.scalars().all()
        return [NoteSchema.model_validate(note) for note in notes_orm]

    async def search_by_project(
        self, project_id: uuid.UUID, user_id: str, skip: int = 0, limit: int = 20
    ) -> list[NoteSchema]:
        stmt = (
            select(NoteModel)
            .where(NoteModel.user_id == user_id, NoteModel.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .order_by(NoteModel.updated_at.desc())
            .options(selectinload(NoteModel.keywords))  # Cargar keywords
        )
        result = await self.session.execute(stmt)
        notes_orm = result.scalars().all()
        return [NoteSchema.model_validate(note) for note in notes_orm]

    async def search_by_keyword_name(
        self,
        keyword_name: str,
        project_id: uuid.UUID | None,  # Puede ser None si no se filtra por proyecto
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[NoteSchema]:
        if not keyword_name.strip():
            return []  # Si el keyword está vacío, retornar lista vacía

        filters = [
            NoteModel.user_id == user_id,
            KeywordModel.name == keyword_name,
        ]
        if project_id is not None:
            filters.append(NoteModel.project_id == project_id)

        stmt = (
            select(NoteModel)
            .join(NoteModel.keywords)  # Hacer join con la tabla de keywords
            .where(*filters)
            .offset(skip)
            .limit(limit)
            .order_by(NoteModel.updated_at.desc())
            .options(selectinload(NoteModel.keywords))  # Cargar keywords
        )
        result = await self.session.execute(stmt)
        notes_orm = result.scalars().all()
        return [NoteSchema.model_validate(note) for note in notes_orm]

    async def search_by_keyword_names(
        self,
        keyword_names: list[str],
        project_id: uuid.UUID,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[NoteSchema]:
        if not keyword_names:
            return []  # Si no hay keywords, retornar lista vacía

        filters = [
            NoteModel.user_id == user_id,
            KeywordModel.name.in_(keyword_names),
            NoteModel.project_id == project_id,  # project_id ya no es opcional
        ]

        stmt = (
            select(NoteModel)
            .join(NoteModel.keywords)  # Hacer join con la tabla de keywords
            .where(*filters)
            .offset(skip)
            .limit(limit)
            .order_by(NoteModel.updated_at.desc())
            .options(selectinload(NoteModel.keywords))  # Cargar keywords
        )
        result = await self.session.execute(stmt)
        notes_orm = result.scalars().all()
        return [NoteSchema.model_validate(note) for note in notes_orm]
