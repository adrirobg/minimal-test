# Persistence Module (Infrastructure)

## Purpose

The `persistence` module, within the `infrastructure` layer, is responsible for all data storage and retrieval concerns for the Kairos BCP application. Its primary goal is to provide concrete implementations for the data repository interfaces (ports) defined in the `core/application/ports/` directory.

This module handles the "how" of data persistence, translating requests from the application layer into operations on the chosen database system (PostgreSQL with pgvector).

## Key Components

* **`sqlalchemy/`**:
    * `models/`: Defines SQLAlchemy ORM models that map to the database tables.
    * `repositories/: Contains concrete implementations of the repository interfaces (e.g., `SQLAlchemyNoteRepositoryImpl`) using SQLAlchemy to interact with PostgreSQL and pgvector for CRUD operations and vector searches.
    * `database.py`: Handles database connection setup, session management, and engine configuration.
* **`migrations/`**: Contains database migration scripts managed by Alembic, allowing for version-controlled evolution of the database schema.

## Interactions

* Implements repository interfaces (ports) from `core/application/ports/`.
* Is called by use cases in the `core/application` layer (via these interfaces).
* Directly uses SQLAlchemy for ORM operations and pgvector functionalities for semantic search against the PostgreSQL database.

## Design Rationale

This module abstracts the data storage mechanism from the rest of the application. By centralizing all database interaction logic here, Kairos BCP can potentially switch database technologies or ORMs with changes localized primarily to this module, minimizing impact on the `core` application logic. This adheres to the principles of Clean Architecture, where infrastructure details are kept separate from business rules.

## Patrón de Unit of Work Dual

### Introducción

El patrón de Unit of Work (UoW) dual implementado en este proyecto tiene como objetivo gestionar las transacciones de base de datos de manera eficiente tanto en contextos síncronos como asíncronos. Proporciona una abstracción sobre las sesiones de base de datos, asegurando que todas las operaciones dentro de una unidad de trabajo se completen con éxito (commit) o se reviertan (rollback) como un todo, manteniendo la consistencia de los datos.

Este enfoque dual permite flexibilidad para diferentes partes de la aplicación, como APIs asíncronas y scripts síncronos, utilizando la implementación más adecuada para cada caso.

### Interfaz Común (`IUnitOfWork`)

La interfaz [`IUnitOfWork`](../../core/application/interfaces/unit_of_work_interface.py:0) define el contrato común para todas las implementaciones de Unit of Work. Establece los métodos esenciales para la gestión de transacciones y el acceso a los repositorios.

```python
# src/pkm_app/core/application/interfaces/unit_of_work_interface.py
from abc import ABC, abstractmethod
from typing import Any, Type

# Adelanta la declaración de INoteRepository para evitar importación circular
# en el contexto de la interfaz.
# from .note_interface import INoteRepository

class IUnitOfWork(ABC):
    notes: Any # Debería ser INoteRepository, pero se usa Any para flexibilidad inicial

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def commit_sync(self):
        raise NotImplementedError

    @abstractmethod
    def rollback_sync(self):
        raise NotImplementedError
```
Esta interfaz permite que el código de la aplicación interactúe con la UoW de manera agnóstica a su implementación específica (síncrona o asíncrona).

### Implementación Asíncrona (`AsyncSQLAlchemyUnitOfWork`)

La clase [`AsyncSQLAlchemyUnitOfWork`](../sqlalchemy/unit_of_work.py:0) es la implementación asíncrona del patrón UoW, diseñada para ser utilizada en entornos que requieren operaciones no bloqueantes, como aplicaciones web construidas con FastAPI.

**Cuándo usarla:**
*   APIs web con FastAPI.
*   Aplicaciones con alta concurrencia que se benefician del modelo `async/await`.
*   Tareas de fondo que realizan operaciones I/O intensivas de forma asíncrona.

**Breve ejemplo de uso (conceptual):**
```python
# En un caso de uso o servicio asíncrono
from src.pkm_app.infrastructure.persistence.sqlalchemy.unit_of_work import AsyncSQLAlchemyUnitOfWork
from src.pkm_app.infrastructure.config.settings import get_settings

async def create_new_note_async(note_data: dict):
    settings = get_settings()
    uow = AsyncSQLAlchemyUnitOfWork(settings.DATABASE_URL_ASYNC)
    async with uow:
        new_note = await uow.notes.add(note_data) # Asumiendo que uow.notes es un AsyncSQLAlchemyNoteRepository
        await uow.commit()
        return new_note
```

### Implementación Síncrona (`SyncSQLAlchemyUnitOfWork`)

La clase [`SyncSQLAlchemyUnitOfWork`](../sqlalchemy/sync_unit_of_work.py:0) es la implementación síncrona del patrón UoW. Es adecuada para contextos donde las operaciones asíncronas no son necesarias o añaden complejidad innecesaria.

**Cuándo usarla:**
*   Scripts de línea de comandos (CLI).
*   Tareas de fondo síncronas.
*   Aplicaciones de interfaz de usuario como Streamlit, si no se está utilizando su manejo de estado asíncrono avanzado.
*   Tests unitarios o de integración que no requieren un bucle de eventos asíncrono.

**Breve ejemplo de uso (conceptual):**
```python
# En un script o tarea síncrona
from src.pkm_app.infrastructure.persistence.sqlalchemy.sync_unit_of_work import SyncSQLAlchemyUnitOfWork
from src.pkm_app.infrastructure.config.settings import get_settings

def process_batch_notes_sync(notes_batch: list):
    settings = get_settings()
    uow = SyncSQLAlchemyUnitOfWork(settings.DATABASE_URL_SYNC)
    with uow:
        for note_data in notes_batch:
            uow.notes.add(note_data) # Asumiendo que uow.notes es un SyncSQLAlchemyNoteRepository
        uow.commit_sync()
```

### Repositorios

Existen dos variantes de repositorios de notas, cada una alineada con su respectiva implementación de Unit of Work:

*   [`AsyncSQLAlchemyNoteRepository`](../sqlalchemy/repositories/note_repository.py:0): Utilizado por `AsyncSQLAlchemyUnitOfWork`. Implementa métodos asíncronos para interactuar con la base de datos.
*   [`SyncSQLAlchemyNoteRepository`](../sqlalchemy/repositories/note_repository.py:0): Utilizado por `SyncSQLAlchemyUnitOfWork`. Implementa métodos síncronos.

Ambos repositorios operan sobre la misma tabla de base de datos (`notes`) y modelos SQLAlchemy, pero difieren en su naturaleza síncrona/asíncrona para encajar con el contexto de la UoW que los utiliza. La UoW correspondiente es responsable de inyectar la sesión de base de datos (síncrona o asíncrona) apropiada al repositorio.

### Guía de Decisión de tipo de Unit of Work

Al decidir qué tipo de Unit of Work utilizar, considera los siguientes factores:

- **Contexto de uso:** (Ej: API web con FastAPI, script de CLI, aplicación de escritorio, tarea de Celery)
- **¿Requiere concurrencia y operaciones I/O no bloqueantes?** (Sí/No)
- **¿El framework o la herramienta principal del contexto es inherentemente asíncrono?** (Sí/No)

| Contexto de Uso         | Concurrencia Requerida | Framework Async | UoW Recomendada          | Justificación                                                                    |
|-------------------------|------------------------|-----------------|--------------------------|----------------------------------------------------------------------------------|
| API FastAPI             | Sí                     | Sí              | `AsyncSQLAlchemyUnitOfWork` | FastAPI está diseñado para async, maximiza el rendimiento.                         |
| Script CLI (simple)     | No                     | No              | `SyncSQLAlchemyUnitOfWork`  | Más simple de implementar y depurar, sin necesidad de bucle de eventos.           |
| Tarea de fondo (Celery) | Depende                | Depende         | `SyncSQLAlchemyUnitOfWork` / `AsyncSQLAlchemyUnitOfWork` | Evaluar si la tarea se beneficia de async; Celery soporta ambas.                |
| UI Streamlit            | No (generalmente)      | No (principalmente) | `SyncSQLAlchemyUnitOfWork`  | Streamlit ejecuta scripts de forma síncrona; async puede añadir complejidad.    |
| Tests Unitarios/Integración | Generalmente No      | Generalmente No | `SyncSQLAlchemyUnitOfWork`  | Más sencillo para configurar y ejecutar tests que no prueban concurrencia.     |
| Jupyter Notebooks (Análisis) | No                   | No              | `SyncSQLAlchemyUnitOfWork`  | Para análisis de datos directos y prototipado rápido.                          |

### Consideraciones Adicionales

*   **Manejo de Errores y Transacciones:** Ambas implementaciones de UoW utilizan contextos (`with` / `async with`) para asegurar que las transacciones se manejen correctamente. Si ocurre una excepción dentro del bloque `with`, la UoW realizará un `rollback` automáticamente. Si no hay excepciones, se realizará un `commit` al final del bloque (o explícitamente si se llama a `commit()` / `commit_sync()` antes).
*   **Impacto en los Tests:** La existencia de UoWs duales implica que los tests de integración deben cubrir ambos flujos (síncrono y asíncrono) para asegurar la correcta funcionalidad. Se pueden utilizar fixtures de Pytest para proporcionar instancias de UoW apropiadas para cada tipo de test. Ver ejemplos en [`test_note_workflow.py`](../../tests/integration/persistence/test_note_workflow.py:0) (asíncrono) y [`test_sync_note_workflow.py`](../../tests/integration/persistence/test_sync_note_workflow.py:0) (síncrono).
*   **Configuración de Base de Datos:** Es crucial que las URLs de conexión a la base de datos (`DATABASE_URL_ASYNC` y `DATABASE_URL_SYNC`) estén configuradas correctamente para cada tipo de UoW, apuntando a los drivers de base de datos adecuados (ej., `postgresql+asyncpg` para asíncrono y `postgresql+psycopg2` para síncrono).
