# Interacción con MCP code-reasoning

## Llamada 1 - Inicio del análisis
**Enviado:**
```xml
<use_mcp_tool>
<server_name>code-reasoning</server_name>
<tool_name>code-reasoning</tool_name>
<arguments>
{
  "thought": "Analizar cómo implementar la vista de Login basándome en el ProjectForm existente",
  "thought_number": 1,
  "total_thoughts": 5,
  "next_thought_needed": true
}
</arguments>
</use_mcp_tool>
```

**Recibido:**
```json
{
  "status": "processed",
  "thought_number": 1,
  "total_thoughts": 5,
  "next_thought_needed": true,
  "branches": [],
  "thought_history_length": 1
}
```

## Llamada 2 - Análisis de ProjectForm
**Enviado:**
```xml
<use_mcp_tool>
<server_name>code-reasoning</server_name>
<tool_name>code-reasoning</tool_name>
<arguments>
{
  "thought": "Analizando ProjectForm.tsx identifico patrones clave: uso de react-hook-form con Zod para validación, estructura de Card para el formulario, y manejo de estados de carga/error. Estos serán la base para LoginForm",
  "thought_number": 2,
  "total_thoughts": 5, 
  "next_thought_needed": true
}
</arguments>
</use_mcp_tool>
```

**Recibido:**
```json
{
  "status": "processed",
  "thought_number": 2,
  "total_thoughts": 5,
  "next_thought_needed": true,
  "branches": [],
  "thought_history_length": 2
}
```

## Llamada 3 - Esquema de validación
**Enviado:**
```xml
<use_mcp_tool>
<server_name>code-reasoning</server_name>
<tool_name>code-reasoning</tool_name>
<arguments>
{
  "thought": "Para el LoginForm necesitamos un esquema Zod que valide: email (requerido, formato email) y password (requerido, mínimo 8 caracteres). Similar a ProjectForm pero más simple al no tener relaciones complejas",
  "thought_number": 3,
  "total_thoughts": 5,
  "next_thought_needed": true
}
</arguments>
</use_mcp_tool>
```

**Recibido:**
```json
{
  "status": "processed",
  "thought_number": 3,
  "total_thoughts": 5,
  "next_thought_needed": true,
  "branches": [],
  "thought_history_length": 3
}
```

## Llamada 4 - Estructura del componente
**Enviado:**
```xml
<use_mcp_tool>
<server_name>code-reasoning</server_name>
<tool_name>code-reasoning</tool_name>
<arguments>
{
  "thought": "El LoginForm seguirá la estructura de Card como ProjectForm pero con: 1) Campo email (Input), 2) Campo password (Input type=password), 3) Botón de submit, 4) Manejo visual de errores, 5) Estado de carga durante el submit",
  "thought_number": 4,
  "total_thoughts": 5,
  "next_thought_needed": true
}
</arguments>
</use_mcp_tool>
```

**Recibido:**
```json
{
  "status": "processed",
  "thought_number": 4,
  "total_thoughts": 5,
  "next_thought_needed": true,
  "branches": [],
  "thought_history_length": 4
}
```

## Llamada 5 - Conexión con store y redirección
**Enviado:**
```xml
<use_mcp_tool>
<server_name>code-reasoning</server_name>
<tool_name>code-reasoning</tool_name>
<arguments>
{
  "thought": "Para completar el LoginForm: 1) Al submit llamar a /api/auth/login con los credenciales, 2) Actualizar el store auth.ts con la respuesta, 3) Redirigir a /dashboard en éxito, 4) Mostrar errores de API si falla",
  "thought_number": 5,
  "total_thoughts": 5,
  "next_thought_needed": false
}
</arguments>
</use_mcp_tool>
```

**Recibido:**
```json
{
  "status": "processed",
  "thought_number": 5,
  "total_thoughts": 5,
  "next_thought_needed": false,
  "branches": [],
  "thought_history_length": 5
}