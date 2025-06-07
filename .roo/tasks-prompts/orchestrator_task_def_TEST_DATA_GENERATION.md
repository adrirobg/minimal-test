# Creación de dataset de prueba para todas las entidades PKM + migración DB para facilitar debugging visual

## Context
**Sistema PKM Kairos BCP**  
El proyecto es un sistema de gestión de conocimiento personal (PKM) que sigue una arquitectura limpia con separación estricta de responsabilidades entre capas (dominio, aplicación, infraestructura).

**Entidades Principales**  
El sistema maneja las siguientes entidades que requieren datos de prueba:
- Notas
- Enlaces entre notas
- Tags/Keywords
- Proyectos
- Fuentes de información
- Perfiles de usuario

**Stack Tecnológico**  
- Backend: Python con SQLAlchemy (ORM) y PostgreSQL (BD)
- Validación: Pydantic
- UI: Streamlit
- Migraciones: Alembic

**Objetivo de los Datos de Prueba**  
Generar datos realistas para:
1. Facilitar el desarrollo y testing de la interfaz de usuario
2. Permitir debugging completo del sistema
3. Validar relaciones entre entidades
4. Probar casos de uso complejos

**Método de Inserción**  
Los datos se cargarán mediante migraciones de Alembic para garantizar:
- Reproducibilidad en diferentes entornos
- Consistencia en el estado inicial de la base de datos
- Integración con el pipeline de CI/CD

## Scope
**Objetivo:**  
Crear un dataset de prueba reducido para validar las relaciones básicas entre entidades PKM, con volúmenes ajustados para uso en desarrollo local.

**Entidades y Cantidades:**
- **Usuarios:** 2 perfiles con características distintas
- **Proyectos:** 
  - 2-3 proyectos por usuario
  - Incluir 1 subproyecto por usuario
- **Notas:** 3-5 notas por proyecto
- **Fuentes:** 1-2 fuentes por usuario  
- **Keywords:** 3-5 keywords por usuario
- **Enlaces:** 1-2 enlaces por nota

**Relaciones y Validaciones:**
- Mantener todas las relaciones definidas entre entidades
- Conservar las validaciones de datos básicas
- Reducir volumen de datos pero mantener cobertura de casos

**Proceso de Migración Simplificado:**
1. Generación básica de datos de prueba
2. Inserción directa en base de datos
3. Eliminados pasos de pre/post migración

## Expected Output
1. **Entregables Esperados**:
   - Scripts Python en `/src/pkm_app/tests/data_generation/`:
     - `generate_test_data.py`: Script principal para generar datos de todas las entidades
     - Entidad-specificos (`notes_data.py`, `projects_data.py`, etc.)
   - Migración SQL en `/src/pkm_app/infrastructure/persistence/migrations/versions/`:
     - Archivo de migración para poblar la base de datos con datos de prueba
   - Archivo de semilla SQL en `/src/pkm_app/infrastructure/persistence/schema/seed.sql`

2. **Criterios de Calidad**:
   - Datos deben cubrir al menos:
     - 3 proyectos
     - 10 notas por proyecto
     - 5 keywords por proyecto
     - Relaciones válidas entre entidades
   - Datos deben ser realistas pero simplificados para debugging
   - Deben soportar los casos de uso principales definidos

3. **Formatos Requeridos**:
   - Scripts en Python 3.10+ (compatible con el proyecto)
   - Migraciones en SQL (Alembic)
   - Documentación en Markdown

4. **Documentación Asociada**:
   - `TEST_DATA_README.md` en `/src/pkm_app/tests/` con:
     - Estructura de los datos generados
     - Instrucciones para ejecución
     - Ejemplos de datos
     - Diagrama de relaciones entre entidades
   - Comentarios en los scripts explicando la lógica de generación

## Additional Resources
#### 1. Archivos de referencia en el proyecto
- **Modelos de dominio**: 
  - `src/pkm_app/core/domain/entities/note.py` - Define estructura base, validaciones y tipos de nota
  - `src/pkm_app/infrastructure/persistence/sqlalchemy/models/note.py` - Modelo SQLAlchemy con relaciones DB

- **DTOs/Esquemas**:
  - `src/pkm_app/core/application/dtos/note_dto.py` - Esquemas Pydantic para API (creación, actualización)

- **Tests existentes**:
  - `src/pkm_app/tests/unit/core/domain/entities/test_note.py` - Ejemplos concretos de datos de prueba válidos/inválidos

#### 2. Documentación técnica
- Tipos de nota válidos: `["markdown", "text", "code", "mixed"]`
- Estructura de metadatos: Diccionario JSON
- Relaciones obligatorias/opcionales (proyectos, fuentes, keywords)

#### 3. Herramientas internas
- **SQLAlchemy**: Para datos relacionados con DB
- **Alembic**: Para migraciones y estructura de tablas
- **Pydantic**: Validación de tipos y estructura de datos

#### 4. Ejemplos de implementación
```python
# Ejemplo de datos válidos (de test_note.py)
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

#### 5. Stack tecnológico clave
- Python 3.10+
- SQLAlchemy (ORM)
- Alembic (migraciones)
- Pydantic (validación)
- PostgreSQL (tipos de datos como JSONB, UUID)

#### 6. Modelos relacionados
- Proyectos (`Project`)
- Fuentes (`Source`)
- Keywords (`Keyword`)
- Usuarios (`UserProfile`)

#### 7. Tests como referencia
- Tests unitarios muestran:
  - Casos válidos/inválidos
  - Validaciones de campos
  - Estructuras de datos esperadas
  - Relaciones entre entidades

---
**Meta-Information**:
- task_id: `[ORCHESTRATOR_WILL_ASSIGN_ID]`
- primary_execution_mode: `code`
- priority: `HIGH`
- dependencies: `None`
- assigned_to: `Orchestrator`