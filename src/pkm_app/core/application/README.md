# Application Sub-Layer

## Purpose

The `application` subdirectory acts as the orchestrator for the Kairos BCP system's features. It contains the application-specific business rules and use cases. Its primary goal is to define and execute the various operations the PKM can perform, such as creating a note, searching for notes, or linking notes.

This sub-layer is responsible for:
* Implementing all use cases of the system.
* Defining the interfaces (ports) that the `infrastructure` layer must implement for external operations (e.g., data persistence, external service calls).
* Mediating data flow between the `domain` entities and the `infrastructure` adapters via Data Transfer Objects (DTOs).

## Key Components

* **`use_cases/`**: Contains classes that implement specific application functionalities (e.g., `CreateNoteUseCase`, `SearchNotesUseCase`). These orchestrate interactions with domain entities and repositories.
* **`dtos/`**: Holds Pydantic models used as Data Transfer Objects for passing structured data between layers, particularly between this `application` layer and the `infrastructure` (UI/API adapters).
* **`interfaces/`**: Defines the abstract interfaces (contracts) for operations that depend on external factors, most notably repository interfaces (e.g., `NoteRepositoryInterface`) which dictate how data should be fetched or stored.

## Interactions

* Depends **only** on the `core/domain` sub-layer to access entities, value objects, and domain services.
* Is called by adapters in the `infrastructure` layer (e.g., UI views, API route handlers).
* Does **not** depend on any concrete implementations within the `infrastructure` layer, only on the interfaces (ports) it defines.

## Design Rationale

This sub-layer acts as a crucial intermediary, decoupling the core domain logic from the specifics of the delivery mechanisms (UI, API) and data storage. This adherence to the Clean Architecture allows for flexibility in how the application is presented or how its data is managed, without affecting the core use cases. Pydantic DTOs ensure clear and validated data contracts.
