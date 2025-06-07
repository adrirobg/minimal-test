# Guía de Desarrollo: Generación de Datos de Prueba PKM

Este documento describe los recursos y consideraciones clave para la generación de datos de prueba para el sistema PKM Kairos BCP.

## Entidades Principales
- Notas
- Enlaces entre notas
- Tags/Keywords
- Proyectos
- Fuentes de información
- Perfiles de usuario

## Stack Tecnológico Relevante
- **Backend**: Python con SQLAlchemy (ORM) y PostgreSQL (BD)
- **Validación**: Pydantic
- **Migraciones**: Alembic

## Archivos de Referencia Clave
- **Modelos de Dominio**:
  - `src/pkm_app/core/domain/entities/note.py`: Estructura base, validaciones y tipos de nota.
  - `src/pkm_app/infrastructure/persistence/sqlalchemy/models/note.py`: Modelo SQLAlchemy con relaciones DB.
- **DTOs/Esquemas**:
  - `src/pkm_app/core/application/dtos/note_dto.py`: Esquemas Pydantic para API (creación, actualización).
- **Tests Existentes**:
  - `src/pkm_app/tests/unit/core/domain/entities/test_note.py`: Ejemplos concretos de datos de prueba válidos/inválidos.

## Consideraciones para la Generación de Datos
- **Tipos de Nota Válidos**: `["markdown", "text", "code", "mixed"]`
- **Estructura de Metadatos**: Diccionario JSON.
- **Relaciones**: Asegurar la integridad referencial entre `UserProfile`, `Project`, `Note`, `Source`, `Keyword`, y `NoteLink`.
- **Volumen de Datos**: Reducido para desarrollo local, pero suficiente para validar relaciones y casos de uso básicos.
  - Usuarios: 2
  - Proyectos: 2-3 por usuario (incluyendo 1 subproyecto)
  - Notas: 3-5 por proyecto
  - Fuentes: 1-2 por usuario
  - Keywords: 3-5 por usuario
  - Enlaces: 1-2 por nota

## Ejemplo de Estructura de Datos (Nota)
```python
{
    "id": uuid.uuid4(),
    "title": "Test Note",
    "content": "Inventar un contenido de prueba",
    "type": "markdown",
    "metadata": {"tags": ["test"]},
    "project_id": uuid.uuid4(),
    "source_id": uuid.uuid4(),
    "keyword_ids": [uuid.uuid4()]
}
```

## Herramientas Internas
- SQLAlchemy para interacción con la base de datos.
- Alembic para la creación de la migración.
- Pydantic para la validación de los datos generados.