<write_file>
<path>src/pkm_app/tests/data_generation/README.md</path>
<content># PKM Test Data Generation

Este directorio contiene los scripts y herramientas para generar datos de prueba realistas para la aplicación PKM (Personal Knowledge Management).

## Descripción General

El sistema de generación de datos de prueba está diseñado para crear un conjunto coherente y realista de datos que incluye:

- **Perfiles de Usuario**: Usuarios con preferencias y configuraciones
- **Proyectos**: Proyectos organizados por usuario
- **Fuentes**: Libros, artículos, sitios web y videos de referencia
- **Palabras Clave**: Tags para categorización de contenido
- **Notas**: Contenido principal con enlaces a proyectos y fuentes
- **Enlaces entre Notas**: Relaciones semánticas entre notas

## Estructura de Archivos

```
data_generation/
├── README.md                 # Este archivo
├── generate_test_data.py     # Script principal de coordinación
├── users_data.py            # Generación de perfiles de usuario
├── projects_data.py         # Generación de proyectos
├── sources_data.py          # Generación de fuentes de información
├── keywords_data.py         # Generación de palabras clave/tags
├── notes_data.py            # Generación de notas
├── note_links_data.py       # Generación de enlaces entre notas
└── sql_generator.py         # Conversión a SQL compatible con el esquema
```

## Uso

### Generar Datos de Prueba

```bash
# Desde el directorio raíz del proyecto
poetry run python -m src.pkm_app.tests.data_generation.generate_test_data
```

Este comando:
1. Genera todas las entidades de datos de prueba
2. Crea un archivo SQL de seed data
3. Genera una migración de Alembic para insertar los datos

### Aplicar Datos a la Base de Datos

```bash
# Aplicar la migración
poetry run alembic upgrade head
```

## Configuración de Datos Generados

### Perfiles de Usuario (3 usuarios)
- Usuarios con emails únicos
- Nombres de display realistas
- Preferencias de configuración (tema, idioma)
- Contexto de aprendizaje inicial

### Proyectos (2-3 por usuario)
- Nombres de proyecto descriptivos
- Descripción del proyecto
- Estado por defecto: "active"
- Metadatos que incluyen el owner_id

### Fuentes (1-2 por usuario)
- Tipos: article, book, website, video
- Títulos realistas según el tipo
- URLs para fuentes web y video
- Metadatos con user_id y descripción

### Palabras Clave (3-5 por usuario)
- Palabras clave únicas por usuario
- Nombres normalizados automáticamente
- Asociadas al usuario propietario

### Notas (2-3 por proyecto)
- Títulos descriptivos
- Contenido párrafo realista
- Tipos: markdown, text, code, mixed
- Enlaces a proyectos y fuentes
- Asociaciones con palabras clave (1-3 por nota)
- Metadatos con tags y user_id

### Enlaces entre Notas (1-2 por nota)
- Tipos de relación: reference, relates_to, depends_on, contradicts, supports
- Evita auto-enlaces
- Preserva información del usuario

## Arquitectura

### Entidades de Dominio
Los generadores utilizan las entidades de dominio reales:
- `UserProfile`: Perfiles de usuario
- `Project`: Proyectos de organización
- `Source`: Fuentes de información
- `Keyword`: Palabras clave/tags
- `Note`: Notas principales
- `NoteLink`: Enlaces entre notas

### Esquema de Base de Datos
El SQL generado es compatible con el esquema real definido en las migraciones de Alembic:
- `user_profiles`: user_id (TEXT) como PK
- `projects`: con user_id y parent_project_id
- `sources`: con user_id, type, description, link_metadata
- `keywords`: con user_id, name
- `notes`: con user_id, note_metadata
- `note_links`: con user_id, description
- `note_keywords`: tabla de asociación

### Generación Coherente
- Los datos mantienen integridad referencial
- Los IDs se generan como UUIDs
- Los timestamps son consistentes
- Las relaciones respetan las restricciones de dominio

## Personalización

### Modificar Cantidades
Puedes ajustar las cantidades en cada generador:

```python
# En generate_test_data.py
users = generate_user_profiles(count=5)  # Más usuarios
projects = generate_projects(users, min_per_user=1, max_per_user=4)  # Más proyectos
```

### Agregar Nuevos Tipos de Datos
1. Crear nuevo archivo `nueva_entidad_data.py`
2. Implementar función `generate_nueva_entidad()`
3. Importar y usar en `generate_test_data.py`
4. Actualizar `sql_generator.py` si es necesario

### Modificar Contenido
- **Faker**: Se usa para generar contenido realista
- **Tipos personalizados**: Modifica las listas de tipos en cada generador
- **Relaciones**: Ajusta la lógica de asociación entre entidades

## Migración y Reversión

### Aplicar Datos
```bash
poetry run alembic upgrade head
```

### Revertir Datos
```bash
poetry run alembic downgrade e9e6a35c39f1
```

Esto eliminará todos los datos de prueba pero mantendrá el esquema de la base de datos.

## Consideraciones

### Desarrollo vs Producción
- Estos datos son **SOLO para desarrollo y testing**
- No usar en producción
- Los datos se regeneran cada vez que se ejecuta el script

### Rendimiento
- La generación es rápida (< 5 segundos)
- Los datos son suficientes para pruebas pero no masivos
- Ideal para desarrollo de frontend y testing de APIs

### Consistencia
- Los UUIDs se generan aleatoriamente en cada ejecución
- Las relaciones se mantienen consistentes
- Los datos de Faker pueden variar pero la estructura se mantiene

## Solución de Problemas

### Error de Migración
Si hay errores al aplicar la migración:
1. Verificar que la base de datos esté corriendo
2. Verificar que las migraciones base estén aplicadas
3. Regenerar los datos si hay problemas de esquema

### Datos Inconsistentes
Si los datos parecen inconsistentes:
1. Regenerar completamente los datos
2. Verificar que las entidades de dominio estén actualizadas
3. Revisar el mapeo en `sql_generator.py`

### Problemas de Schema
Si hay errores de columnas faltantes:
1. Verificar que el esquema real coincida con el SQL generado
2. Actualizar `sql_generator.py` con los nombres correctos de columnas
3. Revisar las migraciones de Alembic para el esquema actual
