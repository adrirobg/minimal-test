import asyncio
import contextlib
from collections.abc import Callable
from types import TracebackType
from typing import Any

from aiocache import Cache, SimpleMemoryCache
from sqlalchemy.ext.asyncio import AsyncSession

from src.pkm_app.core.application.interfaces.keyword_interface import IKeywordRepository
from src.pkm_app.core.application.interfaces.note_interface import INoteRepository
from src.pkm_app.core.application.interfaces.note_link_interface import INoteLinkRepository
from src.pkm_app.core.application.interfaces.project_interface import IProjectRepository
from src.pkm_app.core.application.interfaces.source_interface import ISourceRepository
from src.pkm_app.core.application.interfaces.unit_of_work_interface import IUnitOfWork
from src.pkm_app.infrastructure.persistence.sqlalchemy.database import AsyncSessionLocal
from src.pkm_app.infrastructure.persistence.sqlalchemy.repositories.keyword_repository import (
    SQLAlchemyKeywordRepository,
)
from src.pkm_app.infrastructure.persistence.sqlalchemy.repositories.note_link_repository import (
    SQLAlchemyNoteLinkRepository,
)
from src.pkm_app.infrastructure.persistence.sqlalchemy.repositories.note_repository import (
    SQLAlchemyNoteRepository,
)
from src.pkm_app.infrastructure.persistence.sqlalchemy.repositories.project_repository import (
    SQLAlchemyProjectRepository,
)
from src.pkm_app.infrastructure.persistence.sqlalchemy.repositories.source_repository import (
    SQLAlchemySourceRepository,
)


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        session_factory_or_session: Callable[[], AsyncSession] | AsyncSession = AsyncSessionLocal,
        cache: Cache | None = None,
    ):
        # Permite pasar un sessionmaker o una sesión ya creada
        self._session_factory_or_session = session_factory_or_session
        self._session: AsyncSession | None = None
        self._uow_manages_transaction: bool = False
        self._cache: Cache = cache or SimpleMemoryCache()
        self.notes: INoteRepository
        self.keywords: IKeywordRepository
        self.projects: IProjectRepository
        self.sources: ISourceRepository
        self.note_links: INoteLinkRepository

    async def __aenter__(self) -> "IUnitOfWork":
        """Inicia una nueva sesión y configura los repositorios."""
        # Si es una sesión ya creada, úsala directamente
        if isinstance(self._session_factory_or_session, AsyncSession):
            self._session = self._session_factory_or_session
        else:
            session = self._session_factory_or_session()
            if asyncio.iscoroutine(session):
                self._session = await session
            else:
                self._session = session
        assert self._session is not None

        # Iniciar transacción explícita solo si no hay una activa
        if not self._session.in_transaction():
            await self._session.begin()
            self._uow_manages_transaction = True
        else:
            self._uow_manages_transaction = False

        self.notes = SQLAlchemyNoteRepository(self._session)
        self.keywords = SQLAlchemyKeywordRepository(self._session)
        self.projects = SQLAlchemyProjectRepository(self._session)
        self.sources = SQLAlchemySourceRepository(self._session)
        self.note_links = SQLAlchemyNoteLinkRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Cierra la sesión y maneja excepciones."""
        if not self._session:
            return

        try:
            if (
                exc_type and self._uow_manages_transaction
            ):  # Solo rollback si UoW maneja la transacción
                await self.rollback()
        finally:
            if self._uow_manages_transaction:
                if self._session.in_transaction():  # Asegurar que la transacción del UoW se cierre
                    with contextlib.suppress(Exception):
                        await self._session.rollback()  # Rollback por si no hubo commit o error
                await self._session.close()  # Cerrar la sesión solo si UoW la maneja

            # Siempre limpiar la referencia a la sesión y el flag al salir del contexto del UoW
            self._session = None
            self._uow_manages_transaction = False

    async def commit(self) -> None:
        """Realiza el commit."""
        if not self._session:
            raise RuntimeError("Session no inicializada. Use 'async with'.")
        if self._uow_manages_transaction:  # Solo commit si UoW maneja la transacción
            await self._session.commit()
            # Después de un commit, la transacción se cierra. Si el UoW la maneja,
            # se debe iniciar una nueva para que la sesión siga siendo utilizable
            # dentro del mismo bloque `async with uow`.
            if self._session.is_active:  # pragma: no branch
                await self._session.begin()  # Inicia una nueva transacción controlada por UoW
        else:
            # Si la transacción es externa, el UoW no debe hacer commit.
            # Solo hace flush para persistir cambios en la transacción actual.
            await self._session.flush()

    async def rollback(self) -> None:
        if not self._session:
            raise RuntimeError("Session no inicializada. Use 'async with'.")
        if self._uow_manages_transaction:  # Solo rollback si UoW maneja la transacción
            await self._session.rollback()
            # Después de un rollback, la transacción se cierra. Si el UoW la maneja,
            # se debe iniciar una nueva.
            if self._session.is_active:  # pragma: no branch
                await self._session.begin()  # Inicia una nueva transacción controlada por UoW
        # else:
        # Si la transacción es externa, el UoW no debería hacer rollback.
        # El rollback de la transacción externa se maneja fuera (e.g., en el fixture).
        # No es necesario ni siquiera un flush aquí.
        # await self._session.flush() # No es necesario, podría causar problemas si la transacción externa ya hizo rollback
