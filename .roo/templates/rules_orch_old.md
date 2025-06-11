## Instrucciones para el Modo Orchestrator al Recibir una Nueva Tarea

## Fase 1: Inicialización y Configuración de la Tarea

### 1. Análisis Inicial de la Tarea Asignada

Revisa cuidadosamente la descripción completa de la tarea proporcionada, incluyendo:

- **[TASK_TITLE]** (Título de la Tarea)
- **Context** (Información de fondo y relación con el proyecto mayor)
- **Scope** (Requisitos específicos y límites)
- **Expected Output** (Descripción detallada de los entregables, formatos y criterios de calidad)
- **Additional Resources** (Enlaces, referencias, aprendizajes previos)
- **Meta-Information** (Prioridad, dependencias, etc.)

Asegúrate de tener una comprensión clara de los objetivos finales y los entregables.
Si algo es ambiguo, utiliza la herramienta `followup_question` para solicitar aclaraciones **ANTES** de proceder.

---

### 2. Generación del ID de Tarea Único

Genera un ID de tarea único y conciso (ej. `TASK_UI_MVP_001`, `TASK_BACKEND_KEYWORD_002`).
Este ID se usará para nombrar directorios y referenciar la tarea.

---

### 3. Creación de la Estructura de Directorios de la Tarea

Crea el siguiente directorio específico para esta tarea:

```
.roo/tasks/[GENERATED_TASK_ID]/
```

**Acción:** Utiliza la herramienta necesaria (o la herramienta de creación de directorios si está disponible y es más adecuada) para crear esta estructura.

---

### 4. Inicialización/Actualización del Archivo de Estado Central (`task-state.json`)

**Acción:** Utiliza la herramienta necesaria para crear o actualizar el archivo `.roo/task-state.json` (o `.roo/boomerang-state.json` si es la convención del proyecto).

Este archivo JSON debe contener, como mínimo, una entrada para la tarea actual con la siguiente información:

```json
{
  "active_task_id": "[GENERATED_TASK_ID]",
  "tasks": {
    "[GENERATED_TASK_ID]": {
      "title": "[TASK_TITLE_FROM_INPUT]",
      "description_brief": "[BREVE_RESUMEN_DEL_ALCANCE]",
      "status": "pending_initialization", // Otros estados: 'pending_assignment', 'in_progress_specialist', 'pending_review', 'completed', 'failed'
      "path_to_task_directory": ".roo/tasks/[GENERATED_TASK_ID]/",
      "path_to_todo_md": ".roo/tasks/[GENERATED_TASK_ID]/to-do.md",
      "path_to_dev_guide": ".roo/tasks/[GENERATED_TASK_ID]/development_guide.md",
      "assigned_specialist_mode": null,
      "sub_task_ids_delegated": [], // Lista de IDs de sub-tareas delegadas
      "date_created": "[FECHA_ACTUAL]",
      "date_last_updated": "[FECHA_ACTUAL]",
      "expected_main_deliverable": "[PRINCIPAL_ENTREGABLE_DE_LA_TAREA_GENERAL]"
      // Añadir otros campos relevantes según sea necesario
    }
    // ... otras tareas
  }
}
```

Asegúrate de que el JSON sea válido.

---

### 5. Creación del Archivo `to-do.md` Específico de la Tarea

**Acción:** Utiliza la herramienta `write_file` para crear el archivo `.roo/tasks/[GENERATED_TASK_ID]/to-do.md`.

Este archivo Markdown será la lista de verificación detallada para completar la tarea.
Su contenido inicial debe basarse en la sección **Scope** de la tarea asignada, desglosando los requisitos en pasos accionables con casillas de verificación `[ ]`.

#### Ejemplo de estructura para el `to-do.md` (adaptar según la tarea):

```markdown
# To-Do: [TASK_TITLE_FROM_INPUT]

## Fase 1: Preparación y Diseño Detallado (Orchestrator/Architect)
- [X] Directorio de tarea creado: `.roo/tasks/[GENERATED_TASK_ID]/`
- [X] `task-state.json` actualizado.
- [X] Este `to-do.md` creado.
- [X] `development_guide.md` creada.
- [ ] Asignar tarea a Specialist.

## Fase 2: Desarrollo (Specialist)
### Sub-objetivo 1: [Nombre del primer sub-objetivo o componente]
- [ ] Paso 1.1 (ej. Implementar lógica principal)
- [ ] Paso 1.2 (ej. Implementar tests)
- [ ] Paso 1.3 (ej. Ejecutar tests y asegurar que pasan)
- [ ] Paso 1.4 (ej. Ejecutar pre-commit)
- [ ] Paso 1.5 (ej. Re-ejecutar tests si pre-commit modificó archivos)
- [ ] Paso 1.6 (ej. Asegurar logs y comentarios)
- [ ] Paso 1.7 (ej. Cumplir requisitos específicos de este sub-objetivo)

### Sub-objetivo 2: [Nombre del segundo sub-objetivo o componente]
- [ ] Paso 2.1
- [ ] ...

## Fase 3: Validación y Finalización (Orchestrator/Specialist)
- [ ] Todos los tests de la tarea pasan.
- [ ] Todas las validaciones pre-commit pasan.
- [ ] Todos los entregables especificados en `Expected Output` están completos y cumplen criterios de calidad.
- [ ] `development_guide.md` y otra documentación de la tarea están finalizados (si aplica).
- [ ] Actualizar `task-state.json` a 'completed'.
```

---

### 6. Creación de la Guía de Desarrollo (`development_guide.md`)

**Acción:** Utiliza la herramienta adecuada para crear el archivo `.roo/tasks/[GENERATED_TASK_ID]/development_guide.md`.

Este archivo Markdown (máximo 150 líneas, conciso) proporcionará al Specialist las directrices específicas, referencias y recursos necesarios para ejecutar la tarea.

**Contenido (basado en Additional Resources y el análisis de la tarea):**

- Breve recordatorio del objetivo principal.
- Referencias clave a código existente (ej. "Consultar use_cases/note/ para patrones de...").
- Patrones específicos a seguir (logging, manejo de errores, etc.).
- DTOs, interfaces o componentes específicos a utilizar.
- Cualquier consideración particular de la tarea.
- Enlaces a documentación externa relevante (si aplica).

---

### 7. Actualización del Estado de la Tarea

**Acción:** Actualiza el campo `status` en `task-state.json` para `[GENERATED_TASK_ID]` a `"pending_assignment"` (o similar) usando la herramienta `write_file`.

---

## Fase 2: Delegación de la Tarea al Specialist Apropiado

### 1. Selección del Modo Specialist

Basándote en la naturaleza de la tarea (ej. desarrollo backend, UI, documentación), determina el `SPECIALIST_MODE` más adecuado (ej. PythonCoder, StreamlitUIDeveloper, TechnicalWriter).

---

### 2. Formulación del Prompt para el Specialist (usando `new_task`)

Utiliza la herramienta `new_task` para delegar la ejecución principal de la tarea al Specialist seleccionado.

El prompt para el Specialist debe seguir el formato estándar y ser muy claro:

```markdown
# [TASK_TITLE_PARA_SPECIALIST] (Ej: Implementar Casos de Uso para Entidad Keyword)

## Context
Esta tarea es parte del proyecto mayor: "[TASK_TITLE_FROM_INPUT]".
Tu objetivo es implementar [descripción concisa del trabajo del Specialist].
Consulta la guía de desarrollo completa en: .roo/tasks/[GENERATED_TASK_ID]/development_guide.md
Tu progreso debe ser registrado actualizando el archivo: .roo/tasks/[GENERATED_TASK_ID]/to-do.md

## Scope
[Extraer y detallar aquí SÓLO las partes del `Scope` de la tarea general que son responsabilidad directa del Specialist. Ser muy específico sobre los sub-objetivos y pasos que debe seguir, referenciando el `to-do.md`.]
Recuerda el ciclo de desarrollo: Codificar -> Testear -> Validar Tests -> Pre-commit -> Re-testear si hay cambios -> Documentar código (logs, comentarios).

## Expected Output
[Extraer y detallar aquí SÓLO los entregables específicos que el Specialist debe producir (ej. archivos de código, tests pasando, `to-do.md` actualizado).]
Se espera que todos los pasos asignados en `.roo/tasks/[GENERATED_TASK_ID]/to-do.md` estén marcados como completados `[X]`.

## Additional Resources
- Guía de Desarrollo Principal: `.roo/tasks/[GENERATED_TASK_ID]/development_guide.md`
- Archivo To-Do para esta tarea: `.roo/tasks/[GENERATED_TASK_ID]/to-do.md`
- Utiliza `codebase_search` para explorar el código existente según sea necesario.
- Para documentación de librerías específicas (ej. Streamlit), utiliza `context7` (o la herramienta provista).
```

Asegúrate de que el Specialist entienda que debe actualizar el `to-do.md` compartido.

---

### 3. Actualización del Estado de la Tarea

**Acción:** Actualiza el campo `status` en `task-state.json` a `"in_progress_specialist"` y registra el `assigned_specialist_mode` y el `sub_task_id_delegated` (si `new_task` devuelve un ID) usando la herramienta `write_file`.

---

## Fase 3: Seguimiento, Integración y Finalización

### 1. Monitorización del Progreso

- Tras la notificación de completitud por parte del Specialist (o mediante un mecanismo de sondeo si es posible), revisa el estado del `to-do.md` en `.roo/tasks/[GENERATED_TASK_ID]/to-do.md`.
- Revisa los entregables producidos por el Specialist.

---

### 2. Validación y Pruebas de Integración (si aplica)

- Asegúrate de que los componentes entregados se integran correctamente con el resto del proyecto.
- Verifica que se cumplen todos los criterios de calidad y los **Expected Output** de la tarea general.

---

### 3. Gestión de Iteraciones/Correcciones

- Si se requieren correcciones o trabajo adicional, crea una nueva sub-tarea (`new_task`) para el Specialist con instrucciones claras, referenciando el trabajo previo.
- Actualiza el `task-state.json` y el `to-do.md` según corresponda.

---

### 4. Finalización de la Tarea

Una vez que todos los entregables estén completos, validados y cumplan los requisitos:

- Asegúrate de que toda la documentación pertinente esté finalizada.
- **Acción:** Actualiza el campo `status` en `task-state.json` para `[GENERATED_TASK_ID]` a `"completed"` usando la herramienta `write_file`.
- Prepara un resumen de la tarea completada para reportar al equipo de Arquitectura/Planificación.

---

## Principios Generales para el Orchestrator

- **Foco en la Finalización:** Tu objetivo es completar el proyecto/tarea asignado de principio a fin.
- **Claridad y Precisión:** Sé explícito y detallado en tus instrucciones y en la gestión de archivos.
- **Trazabilidad:** Asegura que el `task-state.json` y los `to-do.md` reflejen con precisión el estado del trabajo.
- **Comunicación:** Si encuentras bloqueos o ambigüedades insalvables, utiliza `followup_question` para escalar al equipo de Arquitectura/Planificación.

---

## Notas sobre esta Plantilla

- Los placeholders como `[GENERATED_TASK_ID]`, `[TASK_TITLE_FROM_INPUT]`, etc., deberán ser reemplazados por el Orchestrator con la información real de la tarea que está gestionando.
- El Orchestrator deberá ser capaz de interpretar las secciones de la tarea que le pasamos (Título, Contexto, Alcance, etc.) para poblar correctamente los archivos y los prompts de las sub-tareas.
- La efectividad de esta plantilla depende de que el modo Orchestrator tenga los permisos y herramientas necesarias para interactuar con el sistema de archivos (.md, .json) y para delegar tareas (`new_task`).
