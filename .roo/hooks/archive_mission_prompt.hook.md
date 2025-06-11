<cognitive_hook id="archive_mission_prompt" version="2.0">
    <description>
        Define la plantilla de prompt estándar que El Oráculo debe usar para delegar la tarea de archivado y aprendizaje al Archivo Central. La plataforma Roo Code se encarga de la indexación automática.
    </description>
    <content type="prompt_template">
        <prompt>
            <mission>Misión de Archivado y Aprendizaje para Tarea `[TASK_ID]`</mission>
            <instruction>
                Tu misión es analizar los artefactos de la tarea completada y destilar el conocimiento adquirido para la mejora continua del Proyecto Cero-Uno. Tu objetivo es consolidar el conocimiento, no fragmentarlo.
            </instruction>
            <workflow>
                <step id="1" name="Análisis de Artefactos">
                    Analiza todos los artefactos en el directorio `.roo/tasks/[TASK_ID]/`, incluyendo el `mission_map.json`, el código final y cualquier ciclo de corrección.
                </step>
                <step id="2" name="Identificación de Lecciones">
                    Identifica patrones, soluciones novedosas, y las causas raíz de cualquier error o ineficiencia. Para cada lección identificada, extrae un "tema" clave (ej. `python_imports`, `async_error_handling`).
                </step>
                <step id="3" name="Consolidación de Conocimiento">
                    Para cada lección y su "tema":
                    1.  Busca en el repositorio de conocimiento `.roo/lessons_learned/` si ya existe un archivo para ese tema (ej. `python_imports.md`).
                    2.  **Si existe:** Usa `apply_diff` o `insert_content` para AÑADIR la nueva lección concisa al archivo existente, en lugar de crear uno nuevo.
                    3.  **Si no existe:** Crea un nuevo archivo `.md` para ese tema y añade la primera lección.
                </step>
                <step id="4" name="Verificación de Formato">
                    Asegúrate de que cada lección añadida o creada sea accionable y esté bien formateada (ej. usando viñetas y ejemplos de código reales de la tarea si es necesario).
                </step>
            </workflow>
        </prompt>
    </content>
</cognitive_hook>