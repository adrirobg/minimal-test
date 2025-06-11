# Core Layer (Domain & Application Logic)

## Purpose

This `core` directory is the heart of the Kairos BCP application. It encapsulates all the business logic, domain knowledge, and application-specific rules, completely independent of any infrastructure concerns like databases, web frameworks, or UI details. Its primary goal is to ensure that the essential complexity of the Personal Knowledge Management (PKM) system is clearly defined and managed in one place, adhering to the principles of Clean Architecture.

This layer is designed to be:
* **Independent:** It has no dependencies on `infrastructure` or any specific external frameworks.
* **Testable:** All logic within can be unit-tested in isolation.
* **Stable:** Changes in external technologies should ideally not force changes here.

## Key Subdirectories

* **`domain/`**: Contains the purest representation of the PKM's business logic, including entities, value objects, and domain services. This is the innermost circle of the Clean Architecture.
* **`application/`**: Orchestrates the data flow and implements the application-specific use cases (features). It defines the interfaces (ports) that the `infrastructure` layer must implement for external interactions (e.g., data persistence).

## Interactions

* The `core` layer (specifically `application`) defines interfaces (ports) that are implemented by the `infrastructure` layer.
* It dictates the operations needed for data persistence (e.g., `NoteRepositoryInterface`) without knowing how they are implemented.
* The `infrastructure` layer depends on `core`, but `core` depends on nothing outside itself.

## Design Rationale

This separation ensures that the core logic of Kairos BCP is robust, maintainable, and adaptable to future changes in technology or requirements. It follows the Clean Architecture principle where dependencies flow inwards.
