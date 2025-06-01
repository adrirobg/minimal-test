# Infrastructure Layer

## Purpose

The `infrastructure` directory contains all the components that interface with the outside world or provide concrete implementations for the abstract ports defined in the `core/application` layer. Its primary goal is to handle all I/O, framework-specific logic, and interactions with external systems (databases, web servers, third-party APIs, file systems, etc.) for the Kairos BCP application.

This layer is where technologies are chosen and implemented. It is the most volatile part of the system, as frameworks and tools may change over time.

## Key Subdirectories

* **`persistence/`**: Contains adaptors for data storage, including SQLAlchemy models, repository implementations for PostgreSQL/pgvector, and database migration scripts (Alembic).
* **`web/`**: Holds adaptors for web interfaces, including views for the Streamlit UI and routers/schemas for the future FastAPI/Flask API.
* **`config/`**: Manages application configuration loading and validation (e.g., using Pydantic BaseSettings).

## Interactions

* Implements the interfaces (ports) defined in `core/application/ports/`.
* Depends on the `core/application` layer to call use cases and pass DTOs.
* Interacts directly with external technologies and frameworks (e.g., PostgreSQL, SQLAlchemy, Streamlit, FastAPI, file system).
* The `core` layer has no knowledge of the concrete implementations within this `infrastructure` layer.

## Design Rationale

This layer acts as the "glue" between the application's core logic and the external world. By isolating all framework-specific code and external dependencies here, the `core` of Kairos BCP remains clean, testable, and independent. This separation allows for easier adaptation to new technologies or changes in external systems without impacting the core business rules. This follows the Clean Architecture's Dependency Inversion Principle.
