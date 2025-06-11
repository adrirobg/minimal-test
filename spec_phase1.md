# Project Specification - Kairos BCP - Phase 1

## Overview

Kairos BCP es una aplicación de Gestión de Conocimiento Personal (PKM) diseñada para permitir a los usuarios capturar, organizar, enlazar y recuperar información de manera eficiente, fomentando una base de conocimiento personal interconectada. La Fase 1 se centrará en establecer las funcionalidades CRUD básicas para Notas y Proyectos, y la capacidad de asociarlos, sentando las bases para futuras expansiones.

## Requirements

### Functional Requirements (Phase 1)

1.  **User Management (Implicit)**:
    *   Todas las entidades (Proyectos, Notas, etc.) deben estar asociadas a un `user_id` para garantizar la propiedad y el aislamiento de los datos del usuario. (La autenticación/gestión de usuarios en sí misma puede estar fuera del alcance de la Fase 1 si se asume un `user_id` fijo para el desarrollo inicial, pero el diseño debe soportarlo).

2.  **Project Management (CRUD)**:
    *   **Create Project**:
        *   Los usuarios pueden crear nuevos proyectos.
        *   Campos obligatorios: `name`.
        *   Campos opcionales: `description`, `parent_project_id` (para jerarquía).
    *   **Read Project(s)**:
        *   Los usuarios pueden ver una lista de todos sus proyectos.
        *   Los usuarios pueden ver los detalles de un proyecto específico (nombre, descripción, notas asociadas, subproyectos).
    *   **Update Project**:
        *   Los usuarios pueden actualizar el `name`, `description`, y `parent_project_id` de sus proyectos existentes.
    *   **Delete Project**:
        *   Los usuarios pueden eliminar sus proyectos. Las notas asociadas tendrán su `project_id` establecido a `NULL`.

3.  **Note Management (CRUD)**:
    *   **Create Note**:
        *   Los usuarios pueden crear nuevas notas.
        *   Campos obligatorios: `content`.
        *   Campos opcionales: `title`, `type`, `note_metadata`, `project_id`, `source_id`, `keywords`.
    *   **Read Note(s)**:
        *   Los usuarios pueden ver una lista de todas sus notas.
        *   Los usuarios pueden ver el contenido completo y los detalles de una nota específica.
    *   **Update Note**:
        *   Los usuarios pueden actualizar todos los campos opcionales de sus notas existentes y su `content`.
    *   **Delete Note**:
        *   Los usuarios pueden eliminar sus notas.

4.  **Note-Project Association**:
    *   Al crear/actualizar una nota, los usuarios pueden asociarla a uno de sus proyectos existentes.
    *   Al visualizar un proyecto, los usuarios pueden ver una lista de todas las notas asociadas a ese proyecto.

5.  **Basic User Workflow**:
    *   El usuario puede crear un proyecto.
    *   Dentro de un proyecto, el usuario puede crear notas.
    *   El usuario puede crear subproyectos dentro de un proyecto.
    *   El usuario puede recuperar y editar notas.
    *   El usuario puede cargar un proyecto y ver todas sus notas y subproyectos.

### Non-Functional Requirements (Phase 1)

1.  **Usability**:
    *   La interfaz de usuario inicial (Streamlit) debe ser intuitiva para las operaciones CRUD básicas de notas y proyectos.
    *   La interfaz de Streamlit debe ser usable en navegadores web modernos.
2.  **Performance**:
    *   Las operaciones CRUD básicas para Notas y Proyectos deben ser perceptualmente rápidas en la interfaz de Streamlit (idealmente < 1-2 segundos para bases de datos con ~1000 notas/100 proyectos).
3.  **Data Integrity**:
    *   Las asociaciones entre notas y proyectos deben mantenerse correctamente.
    *   Las operaciones deben respetar la propiedad del usuario (`user_id`).
4.  **Development Environment**:
    *   El proyecto debe ser desarrollable y ejecutable siguiendo las configuraciones de `pyproject.toml` y `docker-compose.yml`.

## Constraints

1.  **Programming Language**: Python (`>=3.13` según `pyproject.toml`).
2.  **Database**: PostgreSQL (el uso de pgvector para búsqueda semántica es para fases posteriores).
3.  **ORM**: SQLAlchemy (implementación asíncrona).
4.  **Data Validation/Models**: Pydantic.
5.  **Initial UI**: Streamlit.
6.  **Architecture**: Clean Architecture con énfasis modular interno.
7.  **Dependency Management**: Poetry (definido en `pyproject.toml`).
8.  **Async Operations from Streamlit**: La UI de Streamlit deberá gestionar la ejecución de operaciones de backend asíncronas (ej. `asyncio.run()`).
9.  **Testing**: Funcionalidades CRUD principales para Notas y Proyectos deben tener tests de integración básicos.
10. **Embeddings**: El campo `embedding` en la tabla `notes` será ignorado en la Fase 1 (no se generarán ni almacenarán).

## Acceptance Criteria

### Project Management

*   **AC1.1 (Create Project)**: Un usuario puede crear un nuevo proyecto proporcionando un nombre (obligatorio) y descripción (opcional). El proyecto aparece en la lista de proyectos del usuario y se asocia con su `user_id`. `created_at` y `updated_at` se establecen.
*   **AC1.2 (Create Subproject)**: Un usuario puede crear un proyecto asignándole un `parent_project_id` válido (de un proyecto existente del mismo usuario).
*   **AC1.3 (Read Projects List)**: Un usuario puede ver una lista de sus proyectos, mostrando al menos el nombre.
*   **AC1.4 (Read Project Details)**: Al seleccionar un proyecto, se muestran su nombre, descripción, y una lista de títulos/resúmenes de notas asociadas y nombres de subproyectos.
*   **AC1.5 (Update Project)**: Un usuario puede modificar el nombre, descripción y `parent_project_id` de un proyecto existente. `updated_at` se actualiza. Los cambios se reflejan.
*   **AC1.6 (Delete Project)**: Un usuario puede eliminar un proyecto. El proyecto ya no aparece en la lista. Las notas asociadas tienen su `project_id` establecido a `NULL`.

### Note Management

*   **AC2.1 (Create Note)**: Un usuario puede crear una nota con contenido (obligatorio) y opcionalmente título, tipo, metadatos. La nota se asocia al `user_id`. `created_at` y `updated_at` se establecen.
*   **AC2.2 (Create Note in Project)**: Al crear una nota, un usuario puede asociarla a un `project_id` válido de uno de sus proyectos. La nota aparece en la lista de notas de ese proyecto.
*   **AC2.3 (Read Notes List)**: Un usuario puede ver una lista de sus notas, mostrando título/extracto.
*   **AC2.4 (Read Note Details)**: Al seleccionar una nota, se muestra su contenido completo y otros detalles (título, tipo, metadatos, proyecto asociado).
*   **AC2.5 (Update Note)**: Un usuario puede modificar el contenido, título, tipo, metadatos y `project_id` de una nota existente. `updated_at` se actualiza. Los cambios se reflejan.
*   **AC2.6 (Delete Note)**: Un usuario puede eliminar una nota. La nota ya no aparece en las listas.

### General

*   **AC3.1 (User Data Isolation)**: Todas las operaciones CRUD y de listado para notas y proyectos están estrictamente filtradas por el `user_id` del usuario autenticado.

## Edge Cases

1.  **EC1.1 (Invalid Association on Create)**:
    *   Crear nota con `project_id` inexistente o no perteneciente al usuario: Falla la operación, se muestra error.
    *   Crear proyecto con `parent_project_id` inexistente o no perteneciente al usuario: Falla la operación, se muestra error.
2.  **EC1.2 (Duplicate Project Name)**:
    *   Crear proyecto con nombre ya existente para el mismo usuario: Permitido en Fase 1 (según esquema actual sin `UNIQUE` constraint en `user_id, name`).
3.  **EC1.3 (Delete Project with Notes)**:
    *   Eliminar proyecto que contiene notas: El proyecto se elimina, las notas asociadas tienen `project_id` establecido a `NULL`. La UI podría advertir de esto.
4.  **EC1.4 (Cross-User Access Attempt)**:
    *   Cualquier intento de leer/modificar/eliminar entidades de otro `user_id`: La operación falla o la entidad se trata como no existente para el usuario actual.
5.  **EC1.5 (Invalid/Empty Fields)**:
    *   Intentar crear/actualizar con campos obligatorios vacíos (ej. nombre de proyecto, contenido de nota): Pydantic/Validación de BD lo impide, se muestra error en UI.
6.  **EC1.6 (Keyword Re-use)**:
    *   Al crear/actualizar nota con keywords, si un keyword ya existe para el usuario, se reutiliza el existente en lugar de crear un duplicado.
7.  **EC1.7 (Malformed IDs)**:
    *   Proporcionar un ID que no es un UUID válido: Pydantic lo rechaza, se muestra error.
8.  **EC1.8 (Circular Project Hierarchy)**:
    *   Intentar establecer un `parent_project_id` que cree una dependencia circular: La lógica del repositorio de proyectos debe impedirlo y devolver un error.

## Future Considerations
1.  **Search Functionality**: Implementar búsqueda semántica utilizando pgvector para notas y proyectos.
2.  **Advanced Note Features**: Implementar campos adicionales como `embedding`, `source_id`, y `keywords` con lógica de gestión de keywords.
3.  **User Authentication**: Integrar un sistema de autenticación robusto para gestionar `user_id` dinámicamente.
4.  **UI Enhancements**: Mejorar la interfaz de usuario con características como filtrado, ordenación, y visualización de relaciones entre notas y proyectos.
5.  **Performance Optimization**: Evaluar y optimizar el rendimiento de las consultas a medida que la base de datos crezca.
6.  **Testing Framework**: Implementar un marco de pruebas más robusto para cubrir casos de uso y edge cases adicionales.
7.  **Documentation**: Crear documentación detallada para desarrolladores y usuarios finales, incluyendo guías de uso y API.
8.  **Deployment**: Preparar el proyecto para despliegue en entornos de producción, incluyendo configuraciones de seguridad y escalabilidad.
