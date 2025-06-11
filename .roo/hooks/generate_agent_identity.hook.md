<cognitive_hook id="generate_agent_identity">
    <description>
        Define un proceso seguro para generar un nuevo slug y un directorio de reglas para un Agente efímero, evitando colisiones.
    </description>
    <workflow>
        <step id="1">Lee el contenido del archivo `.roomodes`.</step>
        <step id="2">Usa una expresión regular para encontrar todos los slugs que sigan el patrón 'agent-smith-XX'.</step>
        <step id="3">Extrae el número más alto, increméntalo en uno y formatea el nuevo slug (ej. 'agent-smith-02').</step>
        <step id="4">Genera la ruta del directorio de reglas correspondiente (ej. '.roo/rules-agent-smith-02').</step>
        <step id="5">Devuelve el nuevo slug y la ruta del directorio como un objeto JSON.</step>
    </workflow>
</cognitive_hook>