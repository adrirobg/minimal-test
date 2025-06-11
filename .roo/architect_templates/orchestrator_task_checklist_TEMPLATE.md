# Checklist de Definición de Tarea para Orchestrator: [Nombre de la Tarea General a Definir]

## Fase 0: Entendimiento Inicial y Preparación
- [ ] Objetivo principal de la tarea a definir para el Orchestrator comprendido (basado en input del Usuario).
- [ ] Identificadas las principales entidades o componentes del proyecto involucrados.
- [ ] Revisado el archivo `project_coder_profile.md` (o similar, el perfil tecnológico del proyecto) para entender el contexto técnico general.
- [ ] (Opcional) Leídos otros archivos de alto nivel del proyecto (READMEs, docs de arquitectura) si son relevantes para esta tarea.

## Fase 1: Recopilación y Análisis de Información (Iterativo, por sección del Prompt del Orchestrator)

### 1.1. Task Title (para el Orchestrator)
- [ ] Discutido con el Usuario y obtenida la idea central para el título.
- [ ] (Opcional) Delegado al modo `think`: "Sugerir 3-5 opciones concisas y descriptivas para el `Task Title` de una tarea de Orchestrator sobre [tema central]".
- [ ] (Opcional) Output del modo `think` para `Task Title` recibido y revisado.
- [ ] `Task Title` final redactado y confirmado con el Usuario.

### 1.2. Context (para el Orchestrator)
- [ ] Discutido con el Usuario y obtenida la información de fondo, relación con el proyecto mayor, stack tecnológico relevante, y el "por qué" de la tarea.
- [ ] (Opcional) Solicitado al Usuario archivos `.md` adicionales si el contexto es muy complejo y necesita ser documentado.
- [ ] Delegado al modo `think`: "Analizar la siguiente información de contexto [resumen del Architect o referencia a notas/archivos] y estructurar la sección 'Context' para el prompt del Orchestrator, destacando [puntos clave especificados por Architect]".
- [ ] Output del modo `think` para `Context` recibido y revisado.
- [ ] Sección `Context` final redactada y confirmada con el Usuario.

### 1.3. Scope (para el Orchestrator)
- [ ] Discutido con el Usuario y definidos los requisitos específicos, límites de la tarea, y componentes principales a desarrollar/gestionar por el Orchestrator.
- [ ] Identificadas (si las hay) sub-partes del `Scope` que son particularmente complejas o que podrían necesitar un análisis previo por el "think mode del Orchestrator" (el que el Orchestrator mismo puede invocar, no el asistente del Architect). Marcar estas para incluirlas como nota en el prompt del Orchestrator.
- [ ] Delegado al modo `think`: "Desglosar el 'Scope' para la tarea [Nombre Tarea] en pasos lógicos y accionables para el Orchestrator. Considerar el flujo Orchestrator -> PseudoCoder -> Coder. Detallar los sub-objetivos y los pasos del ciclo de desarrollo (Implementar, Tests, Pre-commit) que el Orchestrator deberá asegurar para cada componente. Identificar posibles dependencias o interacciones clave."
- [ ] Output del modo `think` para `Scope` recibido y revisado.
- [ ] Sección `Scope` final redactada y confirmada con el Usuario.

### 1.4. Expected Output (para el Orchestrator)
- [ ] Discutido con el Usuario y detallados los entregables específicos, formatos y criterios de calidad que se esperan al finalizar la tarea del Orchestrator.
- [ ] Delegado al modo `think`: "Definir la sección 'Expected Output' para la tarea [Nombre Tarea], asegurando que los entregables sean medibles y los criterios de calidad sean claros. Considerar todos los artefactos (código, tests, documentación, archivos de estado actualizados)."
- [ ] Output del modo `think` para `Expected Output` recibido y revisado.
- [ ] Sección `Expected Output` final redactada y confirmada con el Usuario.

### 1.5. Additional Resources (para el Orchestrator)
- [ ] Identificadas y listadas las referencias clave (código existente, DTOs, interfaces, perfiles de proyecto, `code_guidelines.md` generales, herramientas como `codebase_search`, `Context7`).
- [ ] (Opcional) Delegado al modo `think`: "Para la tarea [Nombre Tarea] sobre [tema], y considerando el stack [stack_del_proyecto], ¿qué 'Additional Resources' (ejemplos de código específicos a buscar con `codebase_search`, documentación clave de `Context7` a la que el Orchestrator debería apuntar para el PseudoCoder/Coder) serían más pertinentes?"
- [ ] (Opcional) Output del modo `think` para `Additional Resources` recibido y revisado.
- [ ] Sección `Additional Resources` final redactada y confirmada con el Usuario.

### 1.6. Meta-Information (para el Orchestrator)
- [ ] Determinado `priority` con el Usuario.
- [ ] Identificadas `dependencies` con el Usuario.
- [ ] `task_id` se dejará como `[ORCHESTRATOR_WILL_ASSIGN_ID]`.
- [ ] `assigned_to` se establecerá como `Orchestrator` (ya que es el prompt para él).
- [ ] Sección `Meta-Information` final redactada y confirmada con el Usuario.

## Fase 2: Generación del Prompt Final para el Orchestrator
- [ ] Todas las secciones del prompt (Task Title, Context, Scope, Expected Output, Additional Resources, Meta-Information) están completas, redactadas y confirmadas por el Usuario.
- [ ] El prompt completo para el Orchestrator ha sido ensamblado.
- [ ] El prompt final ha sido escrito en el archivo: `.roo/tasks-prompts/[nombre_archivo_prompt_orchestrator].md`.
- [ ] Tarea de definición de prompt completada.