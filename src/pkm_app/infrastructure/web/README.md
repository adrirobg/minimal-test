# Web Adapters Module (Infrastructure)

## Purpose

The `web` module, within the `infrastructure` layer, is responsible for handling all web-related interactions for the Kairos BCP application. This includes serving the user interface and, in the future, exposing an API. Its primary goal is to adapt incoming web requests into calls to the application's use cases and to present the results back to the user or client.

## Key Components

* **`streamlit_ui/`**:
    * `views/`: Contains the Python scripts that define the pages and components of the Streamlit user interface (e.g., `note_view.py`). These scripts will interact with the use cases defined in `core/application/`.
* **`api/` (Future)**:
    * `routers/`: Will contain FastAPI (or Flask) routers defining API endpoints (e.g., `notes_router.py`).
    * `schemas.py`: Will hold Pydantic models used for request and response validation/serialization for the API.

## Interactions

* Receives HTTP requests (directly via Streamlit's mechanism, or via FastAPI/Flask for the API).
* Calls use cases in the `core/application` layer, passing data typically encapsulated in DTOs.
* Receives DTOs or results from the use cases and formats them for presentation in the Streamlit UI or as API responses.

## Design Rationale

This module acts as the entry point for all web-based interactions. By separating the web concerns (UI rendering, API request handling) from the core application logic, Kairos BCP can evolve its web interfaces or add new ones (like a mobile API) with minimal impact on the underlying business rules and use cases. This aligns with the Clean Architecture's goal of making UI details an external plugin to the core application.
