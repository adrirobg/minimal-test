# Development Guide - KAIROS_IMPLEMENTATION_001

## Contexto del Proyecto

### Objetivo Principal
Implementar el **Agente IA "Kairos"** como núcleo inteligente del sistema PKM (Personal Knowledge Management) Kairos BCP. El agente debe integrar:

- **Framework de Agente:** Agno con Python/FastAPI
- **LLM:** API externa Gemini
- **Persistencia:** PostgreSQL para memoria y estado de sesión
- **Herramientas:** RAG sobre base de conocimiento y herramientas CRUD

### Alcance de la Implementación

#### Componentes Principales a Desarrollar

1. **Agente Kairos Core** (`backend/app/agent/`)
   - Configuración del agente Agno con Gemini
   - Gestión de memoria y estado de sesión persistente
   - Lógica de "Análisis Crítico" y "Proactividad"
   - Ciclo ReAct (Reason + Act): Pensamiento → Acción → Observación

2. **Sistema de Herramientas** (`backend/app/agent/tools/`)
   - **RAG Tool:** Búsqueda semántica sobre notas del usuario
   - **CRUD Tools:** Interacción directa con base de datos PKM
   - **Analysis Tools:** Identificación de keywords, resumen de proyectos

3. **API Integration** (`backend/app/api/v1/agent.py`)
   - Endpoint `/chat` para interacción con el agente
   - Gestión de sesiones de conversación
   - Integración con sistema de autenticación existente

4. **Configuración y Persistencia**
   - Migración de persistencia Agno a PostgreSQL
   - Gestión segura de API Keys (Gemini)
   - Configuración de memoria y contexto

#### Flujo Funcional del Agente

```
Input Usuario → [Decisión Herramienta] → [RAG/CRUD/Analysis] → 
[Análisis Crítico] → [Generación Respuesta LLM] → Output Usuario
```

**Características Clave:**
- **Memoria Persistente:** Historial de conversación y preferencias de usuario
- **Herramientas Contextuales:** Acceso inteligente a la base de conocimiento PKM
- **Proactividad:** Sugerencias y análisis no solicitados basados en contexto
- **Análisis Crítico:** Evaluación y síntesis de información recuperada

### Stack Tecnológico Requerido

#### Core del Agente
- **Python 3.13+** con tipado estático
- **Agno Framework** (`pip install agno`)
- **FastAPI** para endpoints de API
- **API Gemini** como LLM principal
- **PostgreSQL** para persistencia de memoria/sesión

#### Herramientas y Librerías
- **SQLAlchemy (async)** para acceso a datos
- **Pydantic v2** para validación y DTOs
- **httpx** para llamadas API externas
- **Poetry** para gestión de dependencias

#### Integración con Sistema Existente
- **Base de Datos:** Reutilizar esquema PostgreSQL existente de Kairos BCP
- **Autenticación:** Integrar con sistema de usuarios existente
- **API:** Extender API v1 existente con endpoints del agente

### Arquitectura y Principios

#### Clean Architecture
- **Dominio:** Entidades del agente (Session, Memory, Tool)
- **Aplicación:** Casos de uso del agente (ProcessChat, ManageMemory)
- **Infraestructura:** Integración Agno, Gemini API, PostgreSQL
- **Interfaz:** FastAPI endpoints y Streamlit UI

#### Principios de Desarrollo
- **Asincronía:** Todos los métodos deben ser async
- **Modularidad:** Herramientas como módulos independientes
- **Observabilidad:** Logging detallado de interacciones del agente
- **Testing:** Cobertura del 90% en lógica central del agente

### Fases de Desarrollo

#### Fase 1: MVP Agente Base
1. **Configuración Agno + Gemini**
   - Integración API Gemini
   - Configuración básica del agente
   - Endpoint `/chat` funcional

2. **Persistencia PostgreSQL**
   - Migración de SQLite a PostgreSQL para Agno
   - Tablas para memoria y sesiones de agente
   - Gestión de estado persistente

3. **Herramienta RAG Básica**
   - Búsqueda básica sobre notas existentes
   - Integración con esquema PKM actual
   - Respuestas contextualizadas

#### Fase 2: Herramientas Avanzadas
1. **CRUD Tools completas**
   - Creación/edición de notas via agente
   - Gestión de proyectos via comandos
   - Operaciones batch inteligentes

2. **Analysis Tools**
   - Identificación automática de keywords
   - Resúmenes de proyectos
   - Análisis de patrones en notas

3. **Lógica Avanzada**
   - Implementación "Análisis Crítico"
   - Comportamiento "Proactivo"
   - Personalización basada en uso

#### Fase 3: Optimización y Escalabilidad
1. **Performance**
   - Optimización de consultas RAG
   - Cache inteligente de respuestas
   - Gestión eficiente de memoria

2. **Observabilidad**
   - Métricas detalladas de uso
   - Debugging de interacciones
   - Logging estructurado

### Criterios de Aceptación

#### Funcionalidades Básicas
- [ ] Usuario puede mantener conversaciones persistentes con el agente
- [ ] Agente puede buscar y recuperar información de notas del usuario
- [ ] Agente recuerda contexto de conversaciones anteriores
- [ ] Respuestas incluyen información relevante de la base de conocimiento

#### Funcionalidades Avanzadas
- [ ] Agente puede crear/editar notas mediante comandos naturales
- [ ] Agente ofrece sugerencias proactivas basadas en patrones
- [ ] Agente identifica y sugiere keywords automáticamente
- [ ] Agente genera resúmenes de proyectos y análisis de contenido

#### Criterios Técnicos
- [ ] Tiempo de respuesta < 5 segundos para consultas básicas
- [ ] Persistencia de sesiones entre reinicios del sistema
- [ ] Integración segura con API Gemini
- [ ] Cobertura de tests >= 90% en lógica del agente
- [ ] Logging completo de todas las interacciones

### Recursos de Desarrollo

#### Documentación de Referencia
- **Especificación Kairos BCP:** `spec_01_especificacion_kairos_bcp.md`
- **Estrategia Framework:** `docs/03_kairos_agent_framework_strategy.md`
- **Plan de Implementación:** `.roo/architect_work/kairos_implementation_plan_checklist.md`

#### Código de Referencia Existente
- **Modelos PKM:** `backend/app/models/` (user, note, project, keyword)
- **Esquemas API:** `backend/app/schemas/` 
- **Endpoints existentes:** `backend/app/api/v1/`
- **Configuración DB:** `backend/app/core/database.py`

#### Estructura de Directorios Objetivo
```
backend/app/agent/
├── __init__.py
├── kairos_agent.py       # Configuración principal del agente Agno
├── memory/
│   ├── __init__.py
│   ├── manager.py        # Gestión de memoria persistente
│   └── models.py         # Modelos de memoria y sesión
├── tools/
│   ├── __init__.py
│   ├── rag_tool.py       # Herramienta de búsqueda RAG
│   ├── crud_tools.py     # Herramientas CRUD para PKM
│   └── analysis_tools.py # Herramientas de análisis
└── config/
    ├── __init__.py
    ├── prompts.py        # Prompts versionados
    └── settings.py       # Configuración específica del agente
```

### Consideraciones Críticas

#### Seguridad
- **API Keys:** Gestión segura de credenciales Gemini
- **Aislamiento:** Cada usuario solo accede a sus datos
- **Validación:** Entrada de usuario siempre validada
- **Logging:** No registrar información sensible

#### Performance
- **Memoria:** Gestión eficiente del contexto de conversación
- **Cache:** Resultados RAG frecuentes cacheados
- **Async:** Todas las operaciones I/O asíncronas
- **Batch:** Operaciones múltiples optimizadas

#### Mantenibilidad
- **Versionado:** Prompts y configuración versionados
- **Modularidad:** Herramientas independientes y testeable
- **Documentación:** Código autodocumentado con docstrings
- **Tests:** Coverage completo de casos de uso y edge cases