# Documento 3: Estrategia del Framework del Agente IA - Kairos (v5)

**1. Objetivo (Purpose):**
* Implementar la lógica central y el comportamiento del Agente IA "Kairos", optimizando para la integración con Postgres para memoria, session, persistencia utilizando las herramientas de Agno y una API LLM externa (ej. Gemini).
* Orquestar la interacción entre el usuario (vía API), el LLM (Gemini), y las herramientas/conocimiento (BCP).
* Gestionar la memoria del agente y el estado de la sesión de forma persistente.

**2. Descripción y Estrategia Funcional (Description & Functional Strategy):**

* **A. Enfoque para el Agente IA:**
    * **Implementación Principal:**
        * El agente se implementa en **Python con FastAPI y framework Agno**, siendo este el núcleo definitivo del agente.
        * Agno está configurado para usar la **API de Gemini**.
        * La persistencia de estado de Agno se migrará a **PostgreSQL**.
        * El frontend interactúa con el endpoint `/chat` en este backend FastAPI/Agno.

* **B. Funcionalidades Clave del Agente (Independiente de la implementación final):**
    * **Ciclo de Vida del Agente:** Procesar input del usuario -> (Opcional) Decidir uso de herramienta/conocimiento -> (Opcional) Llamar herramienta/Recuperar conocimiento de BCP -> Aplicar lógica de "Análisis Crítico" (ver directivas) sobre resultados/contexto -> Generar respuesta con LLM (incorporando "Proactividad" y personalización).
    * **Herramientas (Tools):**
        * **RAG sobre BCP:** Herramienta principal para buscar información relevante en las notas del usuario (vía `search_notes_vector` en Supabase).
        * **Herramientas CRUD BCP (Potencial):** Podría tener herramientas internas para interactuar directamente con la BBDD para leer o  modificar datos de la BCP si una directiva lo requiere. Con Agno, serían `Custom Tools` llamando a las BBDD.
        * **Herramientas de Análisis:** Para funcionalidades como identificar keywords populares, resumir proyectos, etc. serian funciones llamadas por el agente (tools).
    * **Lógica de "Análisis Crítico" y "Proactividad":** Implementar gradualmente según las directivas de Kairos, integradas en el flujo de procesamiento del agente.
    * **Gestión de Memoria y Contexto:** Mantener historial de conversación y preferencias del usuario para personalizar interacciones. (Objetivo: persistir en BBDD Supabase).

**3. Herramientas y Tecnologías (Según la Vía de Implementación):**

* **Vía Agno/FastAPI (MVP Inicial / Fallback):**
    * **Framework Agente:** Agno (`pip install agno`)
    * **Framework API:** FastAPI
    * **Lenguaje:** Python
    * **LLM:** API Externa (ej. Gemini)
    * **Persistencia Estado Agno (MVP):** SQLite
    * **Llamadas API (en Tools):** `httpx`

**4. Plan de Desarrollo (Pasos a Seguir - Development Plan/Steps):**

1.  **Configurar LLM Externo:** Integrar cliente para API Gemini (en Python para Agno/FastAPI). Gestionar API Key de forma segura.
3.  **Desarrollo Agente MVP (Agno/FastAPI):**
    * Configurar Agente Agno con Gemini, persistencia y memoria postgres.
    * Implementar lógica en endpoint `/chat` de FastAPI para interactuar con este agente.
4.  **Iteración Continua (Sobre la plataforma elegida):**
    * Refinar prompts (versionar).
    * Implementar lógica de "Análisis Crítico" y "Proactividad".
    * Desarrollar/mejorar herramientas adicionales.
    * Implementar logging/observabilidad.
    * Probar y refinar interacciones.

**5. Consideraciones Clave (Key Considerations):**
* **Prompt Engineering & Versioning:** Tarea continua y crucial. Prompts deben ser almacenados y versionados (ej. en el repo o en una tabla de Supabase).
* **Observabilidad & Debugging:** Esencial. Utilizar las herramientas de logging y añadir logging detallado en la lógica del agente.
* **Seguridad:**
    * Asegurar las funciones que exponen la lógica del agente.
    * Proteger la API Key de Gemini.
* **Testing:** Estrategia de testing para la lógica del agente, ya sea en Python o TypeScript. Pruebas de integración para los flujos completos.