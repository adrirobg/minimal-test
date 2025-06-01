from abc import abstractmethod
from typing import Any, Protocol, TypeVar, runtime_checkable

from .keyword_interface import IKeywordRepository

# Importar las interfaces de repositorio
from .note_interface import INoteRepository
from .note_link_interface import INoteLinkRepository
from .project_interface import IProjectRepository
from .source_interface import ISourceRepository

RepoType = TypeVar("RepoType", covariant=True)


@runtime_checkable
class IRepository(Protocol[RepoType]):
    """Interfaz base para repositorios."""

    pass


@runtime_checkable
class IUnitOfWork(Protocol):
    """Interfaz para el patrón Unit of Work."""

    notes: INoteRepository
    keywords: IKeywordRepository
    projects: IProjectRepository
    sources: ISourceRepository
    note_links: INoteLinkRepository

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Entra en el contexto asíncrono."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Sale del contexto, manejando excepciones y rollback si es necesario."""
        ...

    @abstractmethod
    async def commit(self) -> None:
        """Confirma las transacciones pendientes."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Revierte las transacciones pendientes."""
        ...
