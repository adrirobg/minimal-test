# Kairos BCP – Project Profile and Technology Stack

## Project Overview
Kairos BCP es una aplicación de Gestión de Conocimiento Personal (PKM) orientada a capturar, organizar, enlazar y recuperar información de manera eficiente, fomentando una base de conocimiento personal interconectada. El sistema prioriza mantenibilidad, modularidad y escalabilidad, siguiendo Clean Architecture y prácticas modernas de desarrollo.

## Core Principles
- Clean Architecture con modularidad interna estricta.
- Separación clara entre dominio, aplicación, infraestructura y UI.
- Código altamente testeable y mantenible.
- Inspiración en proyectos de referencia como fastapi-clean-architecture y modular-monolith-starter-kit.

## Technology Stack

### Lenguaje
- **Python 3.13+** (tipado estático obligatorio, anotaciones en todo el código).

### Backend
- **ORM:** SQLAlchemy (solo modo asíncrono, sin versiones síncronas ni ORMs alternativos).
- **Modelado/Validación:** Pydantic v2 para DTOs, entidades y esquemas de API.
- **Base de datos:** PostgreSQL (pgvector para fases futuras).
- **Gestión de dependencias:** Poetry (no usar requirements.txt).
- **Migraciones:** Alembic (scripts en `infrastructure/persistence/migrations`).
- **Configuración:** Variables de entorno y archivos `.env` (prohibido hardcodear rutas, claves o credenciales).
- **Testing:** Pytest para unitarios e integración, cobertura mínima 90% en core y application.
- **Linters:** Ruff y Black obligatorios.
- **Estructura:** Separación estricta entre `core`, `infrastructure`, `web`, y `tests`.

### UI
- **Framework:** Streamlit (desacoplada del backend, solo interactúa con casos de uso).
- **Restricciones:** Prohibido usar frameworks web distintos a Streamlit (FastAPI solo para fases futuras).

### Infraestructura
- **Contenedores:** Docker y docker-compose para entornos reproducibles.
- **Scripts de migración y seed:** En carpeta correspondiente.

## Coding Guidelines

- Cada archivo debe tener menos de 500 líneas; cada función menos de 50 líneas.
- No incluir lógica de negocio en la UI.
- Los repositorios solo exponen métodos asíncronos.
- Los casos de uso nunca acceden directamente a la infraestructura.
- Prohibido el uso de SQL crudo fuera de los repositorios.
- Los tests deben cubrir casos normales y edge cases definidos en la especificación.
- Los eventos internos deben implementarse usando patrones pub/sub o event dispatcher desacoplados.
- Documentar cada módulo y función pública con docstrings (estándar Google o NumPy).
- Mantener consistencia en nombres, convenciones y estructura de carpetas.

## Quality and Best Practices

- Ejecutar tests antes de finalizar cualquier cambio relevante.
- Usar linters, formateadores y análisis estático en cada commit.
- Mantener la coherencia y alineación con la especificación y el README.
- Prohibido el uso de librerías no aprobadas en pyproject.toml.
