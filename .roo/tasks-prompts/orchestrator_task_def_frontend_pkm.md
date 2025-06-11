# Desarrollo del frontend PKM con React+NextJS, Tailwind y ShadCN para operaciones CRUD

## Context
### Estado Actual del Proyecto
- ✅ **Componentes existentes**:
  - Casos de uso implementados
  - Interfaces definidas
  - DTOs desarrollados
- ⚙️ **Por implementar**:
  - API REST con FastAPI
  - Frontend con React/Next.js

### Objetivos Principales
1. **Desarrollo API**:
   - Implementar endpoints REST basados en DTOs existentes
   - Integrar casos de uso mediante inyección de dependencias
   - Configurar autenticación JWT

2. **Desarrollo Frontend**:
   - Implementar interfaz para gestión jerárquica de proyectos/notas
   - Consumir API mediante servicios dedicados
   - Mantener desacoplamiento mediante contratos DTO

### Stack Tecnológico
| Capa         | Tecnologías                           |
|--------------|---------------------------------------|
| Backend      | FastAPI, PostgreSQL                   |
| Frontend     | React, Next.js, Tailwind CSS, ShadCN  |
| Comunicación | REST API (JSON)                       |

## Scope
#### Fase 1: Implementación API FastAPI
1. **Endpoints CRUD**:
   - Proyectos (/projects)
   - Subproyectos (/projects/{id}/subprojects)
   - Notas (/notes)

2. **Autenticación**:
   - JWT implementation
   - Protected routes

3. **Integración**:
   - Conexión con casos de uso existentes
   - Mapeo DTOs

#### Fase 2: Desarrollo Frontend Core
1. **Estructura Base**:
   - Configuración Next.js con TypeScript
   - Sistema de rutas (app router)
   - Estado global (Zustand)
   - Configuración Tailwind y ShadCN

2. **Componentes Principales**:
   - Vista árbol proyectos (jerárquica)
   - Editor de notas (Markdown)
   - Formularios CRUD para todas las entidades
   - Componentes de navegación

3. **Servicios API**:
   - Clients para todos los endpoints
   - Manejo de errores
   - Tipado TypeScript

#### Fase 3: Integración y Testing
1. **Conexión API-Frontend**:
   - Pruebas de integración
   - Manejo de estados de carga/error
   - Actualización en tiempo real

2. **Testing**:
   - Unit tests (Jest)
   - Integration tests (React Testing Library)
   - E2E tests (Playwright)

## Expected Output
#### 1. Entregables Técnicos
- **API FastAPI**:
  - Endpoints RESTful para todas las entidades
  - Autenticación JWT integrada
  - Documentación Swagger/OpenAPI

- **Frontend Next.js**:
  - Vistas CRUD completas
  - Sistema de enrutamiento dinámico
  - Gestión de estado

- **Servicios de Integración**:
  - Conexión API-Frontend
  - Integración con servicios externos

#### 2. Criterios de Calidad
- **Tests**: 80% cobertura backend, 70% frontend
- **Documentación**: Swagger, JSDoc/TSDoc, ADRs
- **Estándares**: PEP8, ESLint, WCAG 2.1 AA

#### 3. Artefactos Adicionales
- Configuración entorno desarrollo (.env)
- Documentación básica de usuario

#### 4. Validación
- Pruebas E2E con Playwright
- 100% código revisado

## Additional Resources
1. **FastAPI**:
   - Documentación oficial FastAPI
   - Ejemplos de autenticación JWT
   - Configuración CORS para Next.js

2. **Next.js**:
   - Documentación App Router
   - Ejemplos de consumo de API
   - Configuración Tailwind + ShadCN

3. **ShadCN Components (USAR SERVIDOR MCP @21st-dev/magic OBLIGATORIAMENTE)**:
   - Componentes para formularios CRUD (usar /ui o /21)
   - Tree view para jerarquía proyectos
   - Editor de markdown
   - Acceso a repositorio de componentes mediante MCP

4. **Testing**:
   - Configuración Playwright
   - Ejemplos pruebas E2E para APIs

5. **Código Existente**:
   - DTOs en `src/pkm_app/core/application/dtos`
   - Interfaces en `src/pkm_app/core/application/interfaces`
   - Casos de uso en `src/pkm_app/core/application/use_cases`

---
**Meta-Information**:
- task_id: `[ORCHESTRATOR_WILL_ASSIGN_ID]`
- primary_execution_mode: `code`
- priority: `HIGH`
- dependencies: `None`
- assigned_to: `Orchestrator`