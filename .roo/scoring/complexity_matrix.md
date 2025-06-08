<!-- 
    Rúbrica de Puntuación de Complejidad de Tarea (TCS) v2.0
    Instrucciones para el agente que la ejecuta (PseudoCoder):
    1. Parsear este documento XML.
    2. Iterar sobre cada <metric>.
    3. Ejecutar la <instruction> contenida en cada métrica sobre el contexto de la tarea actual.
    4. Si la condición de la instrucción se cumple, sumar los puntos del atributo "points".
    5. Comparar la suma total con el <threshold> para determinar la <strategy> a seguir.
-->

<complexity_rubric name="Task Complexity Score v2.0">
    <dimension name="Novedad y Conocimiento Requerido">
        <metric id="NOV-01" points="3">
            <instruction>
                Analiza las tecnologías clave mencionadas en la 'development_guide.md'. Para cada una, consulta al `Memory` mode si existen 'lecciones aprendidas' o tareas pasadas. Si alguna tecnología principal no tiene precedentes, esta métrica se cumple.
            </instruction>
        </metric>
        <metric id="NOV-02" points="2">
            <instruction>
                Analiza el 'Scope' de la tarea. Si menciona explícitamente la aplicación de un patrón de diseño complejo (ej. 'Circuit Breaker', 'Event Sourcing', etc.) que no es un estándar del proyecto, esta métrica se cumple.
            </instruction>
        </metric>
    </dimension>
    <dimension name="Interdependencia y Acoplamiento">
        <metric id="CPL-01" points="3">
            <instruction>
                Identifica y cuenta el número de módulos/entidades de dominio únicos mencionados en el 'Scope' y 'Additional Resources'. Si el número es superior a 3, esta métrica se cumple.
            </instruction>
        </metric>
        <metric id="CPL-02" points="1">
            <instruction>
                Identifica y cuenta el número de módulos/entidades de dominio únicos mencionados en el 'Scope' y 'Additional Resources'. Si el número está entre 2 y 3 (inclusive), esta métrica se cumple.
            </instruction>
        </metric>
    </dimension>
    <dimension name="Escala y Amplitud">
        <metric id="SCL-01" points="2">
            <instruction>
                Analiza el 'Expected Output' y el 'Scope'. Cuenta el número de nuevos archivos de código (excluyendo tests) que se deben crear. Si el número es superior a 5, esta métrica se cumple.
            </instruction>
        </metric>
        <metric id="SCL-02" points="1">
            <instruction>
                Analiza el 'Expected Output' y el 'Scope'. Cuenta el número de nuevos archivos de código (excluyendo tests) que se deben crear. Si el número está entre 2 y 5 (inclusive), esta métrica se cumple.
            </instruction>
        </metric>
    </dimension>
    <dimension name="Ambigüedad y Abstracción">
        <metric id="AMB-01" points="3">
            <instruction>
                Busca en el 'Scope' y 'Task Title' la presencia de palabras clave de alto nivel como "diseñar", "arquitectura", "refactorizar sistema", "crear nuevo módulo desde cero". Si se encuentra alguna, esta métrica se cumple.
            </instruction>
        </metric>
        <metric id="AMB-02" points="1">
            <instruction>
                Busca en el 'Scope' la palabra clave "investigar". Si se encuentra, esta métrica se cumple.
            </instruction>
        </metric>
    </dimension>
    <scoring_logic>
        <threshold value="4" comparison="greater_or_equal">
            <strategy>ToT</strategy>
            <description>La tarea se considera COMPLEJA y requiere exploración de múltiples planes.</description>
        </threshold>
        <default_strategy>
            <strategy>CoT</strategy>
            <description>La tarea se considera ESTÁNDAR y se puede abordar con un plan directo.</description>
        </default_strategy>
    </scoring_logic>
</complexity_rubric>