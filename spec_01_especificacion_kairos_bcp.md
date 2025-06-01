# Especificación SPARC – Kairos BCP (Fase 1)

## 1. Visión

Kairos BCP es una aplicación de Gestión de Conocimiento Personal (PKM) que permite a los usuarios capturar, organizar, enlazar y recuperar información de manera eficiente, fomentando una base de conocimiento personal interconectada. El sistema prioriza la mantenibilidad, modularidad y escalabilidad, siguiendo la Arquitectura Limpia y prácticas modernas de desarrollo.

## 2. Requisitos Funcionales

### 2.1. Gestión de Proyectos (CRUD)
- Crear, leer, actualizar y eliminar proyectos.
- Campos obligatorios: `name`.
- Campos opcionales: `description`, `parent_project_id` (jerarquía).
- Subproyectos soportados mediante `parent_project_id`.
- Al eliminar un proyecto, las notas asociadas quedan sin proyecto (`project_id` a `NULL`).

### 2.2. Gestión de Notas (CRUD)
- Crear, leer, actualizar y eliminar notas.
- Campos obligatorios: `content`.
- Opcionales: `title`, `type`, `note_metadata`, `project_id`, `source_id`, `keywords`.
- Las notas pueden asociarse a proyectos existentes.

### 2.3. Asociación Nota-Proyecto
- Al crear/editar una nota, puede asociarse a un proyecto.
- Al visualizar un proyecto, se listan sus notas asociadas.

### 2.4. Flujo Básico de Usuario
- Crear proyectos y subproyectos.
- Crear notas dentro de proyectos.
- Recuperar y editar notas.
- Visualizar proyectos con sus notas y subproyectos.

### 2.5. Gestión de Usuario (Implícita)
- Todas las entidades están asociadas a un `user_id`.
- El diseño soporta multiusuario, aunque la autenticación puede ser simulada en Fase 1.

## 3. Requisitos No Funcionales

- **Usabilidad:** UI inicial en Streamlit, intuitiva y usable en navegadores modernos.
- **Rendimiento:** Operaciones CRUD rápidas (<2s con ~1000 notas/100 proyectos).
- **Integridad de datos:** Asociaciones y propiedad de usuario siempre respetadas.
- **Entorno de desarrollo:** Configuración reproducible vía `pyproject.toml` y `docker-compose.yml`.
- **Testeabilidad:** Tests unitarios y de integración desde el inicio.
- **Calidad:** Uso de linters, formateadores y análisis estático.

## 4. Criterios de Aceptación

### Proyectos
- Crear, listar, ver detalles, actualizar y eliminar proyectos/subproyectos.
- Al eliminar un proyecto, las notas asociadas quedan sin proyecto.

### Notas
- Crear, listar, ver detalles, actualizar y eliminar notas.
- Asociar notas a proyectos válidos del usuario.

### General
- Todas las operaciones CRUD filtradas por `user_id`.
- Tiempos de respuesta adecuados.
- Validación de campos obligatorios y relaciones.

## 5. Restricciones

- **Lenguaje:** Python (>=3.13).
- **Base de datos:** PostgreSQL (pgvector para fases futuras).
- **ORM:** SQLAlchemy (async).
- **Modelado/Validación:** Pydantic.
- **UI:** Streamlit.
- **Arquitectura:** Clean Architecture, modularidad interna.
- **Gestión dependencias:** Poetry.
- **Async en UI:** Uso de `asyncio.run()` en Streamlit.
- **Testing:** CRUD de notas y proyectos debe tener tests de integración.
- **Embeddings:** El campo `embedding` en notas se ignora en Fase 1.

## 6. Casos Límite

- Asociación inválida de notas/proyectos (IDs inexistentes o de otro usuario): error.
- Nombres de proyecto duplicados: permitidos en Fase 1.
- Eliminación de proyecto con notas: notas quedan sin proyecto.
- Acceso cruzado entre usuarios: prohibido.
- Campos obligatorios vacíos: error de validación.
- Reutilización de keywords existentes.
- IDs malformados: error de validación.
- Jerarquía circular de proyectos: prohibida.
- Integridad y aislamiento de datos por usuario.

## 7. Consideraciones Futuras

- Búsqueda semántica con pgvector.
- Gestión avanzada de keywords y embeddings.
- Autenticación robusta y gestión dinámica de usuarios.
- Mejoras de UI: filtrado, ordenación, visualización de relaciones.
- Optimización de rendimiento para grandes volúmenes.
- Marco de pruebas ampliado.
- Documentación para desarrolladores y usuarios.
- Preparación para despliegue seguro y escalable.
