# Domain Sub-Layer

## Purpose

The `domain` subdirectory represents the very center of the Clean Architecture for Kairos BCP. It contains the enterprise-wide business rules and data structures that are fundamental to the Personal Knowledge Management (PKM) system. The goal is to encapsulate the most stable and high-level policies of the application.

This sub-layer contains:
* **Entities:** Objects representing core business concepts (e.g., a Note, a Link), each with its own identity and encapsulating critical business logic.
* **Value Objects:** Immutable objects that describe attributes of entities (e.g., an EmbeddingVector) and do not have a conceptual identity.
* **Domain Services:** Logic that doesn't naturally fit within a single entity but is still part of the core domain rules, often coordinating multiple entities.

## Key Components

* **`entities/`**: Directory containing Pydantic models that define the structure and validation rules for domain entities (e.g., `note.py`, `link.py`).
* **`value_objects/`**: Directory for Pydantic models representing value objects (e.g., `note.py`).
* **`services/`**: Directory for domain services (e.g., `linking_service.py` for complex link consistency logic).

## Interactions

* This `domain` sub-layer has **no dependencies** on any other layer or sub-layer within the application. It is completely self-contained.
* Entities and value objects are used by the `application` sub-layer (specifically by use cases) and by domain services within this sub-layer.

## Design Rationale

By keeping this sub-layer pure and free of external dependencies, we ensure that the fundamental business rules of Kairos BCP are protected from changes in technology or application-specific logic. This maximizes the stability and reusability of the core domain knowledge. Pydantic is used here for robust data definition and validation.
