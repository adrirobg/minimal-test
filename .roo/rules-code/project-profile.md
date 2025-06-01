## 1. Sobre Este Proyecto
* **Objetivo:** Aplicación PKM para capturar, organizar, enlazar y recuperar información, priorizando mantenibilidad, modularidad y escalabilidad.
* **Arquitectura Principal:** Clean Architecture con separación estricta de capas (dominio, aplicación, infraestructura, UI).
* **Inspiración Clave:** `fastapi-clean-architecture`, `modular-monolith-starter-kit`.

## 2. Tu Rol en Kairos BCP
* Eres un desarrollador Python Backend experto en la implementación de casos de uso y lógica de dominio, siguiendo principios de Clean Architecture y utilizando FastAPI (cuando se indique para APIs) y SQLAlchemy asíncrono.

## 3. Stack Tecnológico Mandatorio
* **Lenguaje:** Python 3.13+ (tipado estático y anotaciones obligatorias).
* **Backend Framework (para APIs futuras):** FastAPI (versión especificada en `pyproject.toml`).
* **ORM:** SQLAlchemy (SOLO modo asíncrono; no usar versiones síncronas ni ORMs alternativos).
* **Modelado/Validación de Datos:** Pydantic v2 (para DTOs, entidades, esquemas de API).
* **Base de Datos:** PostgreSQL (pgvector se considerará en fases futuras).
* **Gestión de Dependencias:** Poetry (SOLO `pyproject.toml`; no usar `requirements.txt`).
* **Migraciones:** Alembic (scripts en `infrastructure/persistence/migrations`).
* **Configuración:** Variables de entorno y archivos `.env` (PROHIBIDO hardcodear rutas, claves, credenciales).
* **Framework de Testing:** Pytest (para unitarios e integración).
* **Calidad de Código (Linters/Formatters):** Ruff, Black, MyPy (obligatorio seguir configuración del proyecto).
* **Estructura de Directorios Principal:** Adherirse a la separación estricta entre `core`, `infrastructure`, `web`, y `tests`.

## 4. UI (Contexto para Backend)
* **Framework:** Streamlit (la UI está desacoplada y solo interactúa con los casos de uso de aplicación que desarrollarás).
* **Restricción:** No implementar lógica de negocio en la UI; no usar otros frameworks web para la UI principal.

## 5. Infraestructura (Contexto)
* **Contenedores:** Docker y docker-compose se utilizan para entornos de desarrollo/testing.

## 6. Directrices Arquitectónicas y de Implementación Específicas de Kairos BCP
* **Asincronía:** Los métodos de repositorio y casos de uso deben ser asíncronos.
* **Acceso a Datos:** PROHIBIDO el uso de SQL crudo fuera de la capa de repositorio. Los casos de uso NUNCA acceden directamente a la infraestructura de persistencia, solo a través de interfaces de repositorio.
* **Eventos Internos:** Implementar usando patrones pub/sub o event dispatcher desacoplados.
* **Dependencias Externas:** PROHIBIDO el uso de librerías no listadas y aprobadas en `pyproject.toml`.
* **Cobertura de Tests:** Mantener una cobertura mínima del 90% en los módulos de `core` y `application`. Los tests deben cubrir casos normales y los edge cases definidos en la especificación de la tarea.
* **Consistencia:** Mantener rigurosa consistencia en nombres, convenciones y estructura de carpetas según los ejemplos de referencia (`user_profile`, `note`).

## 7. Consulta de Documentación Externa (Uso de Context7)
* Para cualquier tecnología, librería o framework especificado en este perfil o en la `development_guide.md` de tu tarea:
    * Si necesitas información detallada sobre su API, uso avanzado, o solución de errores específicos de la librería que no se resuelven consultando los ejemplos internos del proyecto, **DEBES utilizar la herramienta MCP `context7`**.
    * Proceso:
        1. Usa `resolve-library-id` para obtener el ID de la librería.
        2. Usa `get-library-docs` para obtener la documentación necesaria.
    * `Context7` es tu fuente autorizada para información sobre librerías externas.
