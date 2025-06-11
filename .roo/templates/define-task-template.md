
# Plantilla para Definir una Tarea


**Mi objetivo principal:** Necesito tu ayuda experta para definir, desarrollar y refinar exhaustivamente una nueva tarea. Partiremos de una funcionalidad específica que necesito. Esta tarea será posteriormente gestionada por el Orchestrator y, finalmente, ejecutada por un Specialist (probablemente un Coder). Es absolutamente crucial que la descripción de la tarea sea lo más clara, concreta, bien orientada, inequívoca y completa posible. Queremos minimizar la ambigüedad y maximizar la probabilidad de que el Specialist IA genere una solución correcta, eficiente y de alta calidad a la primera.

**Mi idea inicial/funcionalidad específica es:**
" [AQUÍ INSERTARÁS TU IDEA INICIAL/FUNCIONALIDAD ESPECÍFICA.
Ejemplo 1: "Necesito un script en Python que automatice la copia de seguridad diaria de una base de datos PostgreSQL a un bucket S3, asegurando que se creen logs de la operación y se envíe una notificación por email en caso de fallo."
Ejemplo 2: "Quiero añadir una nueva funcionalidad a nuestra aplicación web (stack: React, Node.js, MongoDB) que permita a los usuarios exportar sus datos de perfil en formato CSV, incluyendo tests unitarios para la lógica de exportación y documentación de la nueva API endpoint."] "

**Tu Misión como Architect:**
1.  **Análisis Inicial:** Basándote en mi funcionalidad específica, identifica las áreas clave que necesitan mayor elaboración.
2.  **Interrogación Guiada y Uso de Herramientas:** Condúceme a través de un proceso de preguntas estructuradas para obtener toda la información necesaria para rellenar cada sección del formato de tarea estándar.
    * **Para ello, cuando necesites hacerme una pregunta para obtener detalles o aclarar información, DEBERÁS utilizar la herramienta `follow_up_question`. Por ejemplo: `follow_up_question("¿Podrías detallar cuál es el proyecto más grande al que pertenece esta tarea y sus objetivos principales?")`**.
    * No asumas nada; pregunta explícitamente usando `follow_up_question`. Ayúdame a pensar en los detalles que podría haber pasado por alto.
    * Para el `Context`: Pregúntame sobre el proyecto más grande, el "por qué" de esta tarea, los objetivos de negocio o técnicos que persigue. **Si la tarea debe respetar un stack tecnológico definido del proyecto y crees que puedes tener acceso a esa información, intenta utilizarla. Si no, usa `follow_up_question` para preguntarme al respecto.**
    * Para el `Scope`: Ayúdame a definir límites claros (qué está dentro y qué está fuera), los requisitos específicos y funcionales. **Considera que las tareas suelen ser para crear funcionalidades desde cero dentro de una aplicación existente.** Si es apropiado, ayúdame a desglosar la tarea en `Step-by-step instructions` lógicas y accionables para el Specialist, incluyendo pasos como la ejecución de validaciones pre-commit y la confirmación del éxito de los tests.
    * Para el `Expected Output` (esta sección es **crítica** y a menudo la más desafiante para mí): Guíame para detallar meticulosamente:
        * El **código fuente** de la funcionalidad.
        * **Tests unitarios (y/o de integración)** que cubran los principales casos de uso y casos límite, junto con la **confirmación de que todos los tests pasan con éxito**.
        * La **ejecución exitosa de las validaciones pre-commit** configuradas en el proyecto (si aplica, y si hay cambios, la re-ejecución y confirmación de tests).
        * **Logs adecuados** implementados en el código para el seguimiento y la depuración.
        * **Comentarios claros y pertinentes** en el código.
        * **Documentación técnica** de la funcionalidad desarrollada (ej: Javadoc, PHPDoc, comentarios en API, o un archivo README específico).
        * Cualquier otro **artefacto o formato específico** requerido.
        * **Criterios de calidad objetivos** que el código y los entregables deben cumplir (ej: rendimiento, seguridad, mantenibilidad, cumplimiento de estándares de codificación del proyecto).
    * Para `Additional Resources`: Pregúntame si existen ejemplos, documentación del stack tecnológico del proyecto, APIs existentes que deba usar, aprendizajes de tareas previas, o cualquier material que pueda ayudar al Specialist.
    * Para `Meta-Information`: Ayúdame a determinar un `SPECIALIST_MODE` adecuado (ej: PythonCoder, JavaBackendDeveloper), una `priority` razonable, y a identificar posibles `dependencies`. El `task_id` se asignará posteriormente.
3.  **Claridad y Precisión:** En cada pregunta (formulada vía `follow_up_question`) y en la interpretación de mis respuestas, enfócate en la precisión y en evitar la ambigüedad. Si una respuesta mía es vaga, utiliza `follow_up_question` para pedirme que la concrete o que proporcione ejemplos.
4.  **Sugerencias y Mejores Prácticas:** Si ves oportunidades para mejorar la definición de la tarea, plantear enfoques alternativos (sin entrar en la implementación detallada), o aplicar mejores prácticas de ingeniería de software en la definición, por favor, sugiérelas.
5.  **Síntesis Final:** Una vez que consideres que hemos cubierto todos los aspectos y que la información es suficiente y de alta calidad, genera la descripción completa de la tarea utilizando el formato estándar.

**Formato de Tarea Estándar (para tu referencia al generar la salida final):**
```
# [Task Title]

## Context
[Background information and relationship to the larger project. Include details about the existing project tech stack if relevant and known.]

## Scope
[Specific requirements and boundaries for the task, often involving creating new functionality. Include step-by-step instructions when appropriate, covering development, testing, pre-commit checks, etc.]

## Expected Output
[Detailed description of ALL deliverables:
- Code for the functionality.
- Comprehensive tests (unit, integration) WITH CONFIRMATION OF SUCCESSFUL EXECUTION.
- Proof of successful pre-commit validation (if applicable, including re-testing after changes).
- Adequate logging implemented.
- Clear and appropriate code comments.
- Technical documentation.
- Format specifications for all deliverables.
- Objective quality criteria.]

## Additional Resources
[Relevant tips or examples. Links to reference materials, project's tech stack documentation, existing APIs, previous learnings from similar tasks.]

---

**Meta-Information**:
- task_id: [TO_BE_GENERATED_LATER]
- assigned_to: [SPECIALIST_MODE]
- priority: [LOW|MEDIUM|HIGH|CRITICAL]
- dependencies: [LIST_OF_DEPENDENT_TASK_IDS]
```

**Por favor, comienza. Analiza mi funcionalidad específica inicial y utiliza `follow_up_question` para plantearme tus primeras preguntas, enfocándote en dar forma al `Task Title` y al `Context`.** Estoy listo para colaborar contigo.
