<cognitive_hook id="mission_map_schema">
    <description>
        Define el esquema JSON estándar para un "Mapa de Misión". Este mapa es un grafo de tareas ejecutable por El Oráculo.
    </description>
    <content type="json_schema">
        {
          "project": "String - Nombre del Proyecto General",
          "phases": [
            {
              "phase_id": "String - Identificador de la Fase (ej. 'Phase_1_Backend_API')",
              "description": "String - Descripción de los objetivos de esta fase.",
              "tasks": [
                {
                  "task_id": "String - Identificador único de la tarea (ej. '1.1_create_user_endpoints')",
                  "description": "String - Descripción concisa de la tarea.",
                  "agent_profile": "String - Perfil del Agente requerido (ej. 'agent:python-fastapi').",
                  "dependencies": [
                    "String - Lista de task_id de las que depende esta tarea."
                  ],
                  "artifacts_output": [
                    "String - Lista de rutas a los archivos que se espera que esta tarea genere o modifique."
                  ],
                  "validation_criteria": "String - Descripción de cómo se validará el éxito de la tarea.",
                  "human_checkpoint": "Boolean - Si es 'true', El Oráculo debe pausar y pedir aprobación humana después de esta tarea."
                }
              ]
            }
          ]
        }
    </content>
</cognitive_hook>