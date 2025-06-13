# Sistema de Logging Híbrido - Kairos BCP

## Descripción
Sistema de tracking y logging para el desarrollo experimental de Kairos BCP usando metodología Roo Code + Context7 + Mission Map.

## Estructura de Archivos

### Archivos Core
- **mission_map.json**: Configuración principal con todas las tareas
- **CURRENT_STATE.md**: Estado actual del proyecto para Claude Code
- **scripts/generate_todo.py**: Generador automático de TODO.md

### Archivos de Logging (logs/)
- **todo.md**: TODO generado automáticamente desde mission_map.json
- **progress_log.md**: Log de progreso que Claude Code actualiza
- **context7_usage.md**: Tracking de uso de Context7
- **artifacts_created.md**: Lista de archivos/componentes creados

## Flujo de Trabajo

### Para Claude Code
1. Leer CURRENT_STATE.md para contexto
2. Revisar logs/todo.md para tareas pendientes
3. Ejecutar tarea con Context7
4. Logear progreso en logs/progress_log.md
5. Actualizar status en logs/todo.md

### Para Desarrollador (Humano)
1. Ejecutar setup: ./scripts/setup_logging.sh
2. Crear rama experimental: git checkout -b experiment-rewrite-v1
3. Iniciar Claude Code con contexto
4. Revisar logs para debugging
5. Reset si es necesario: git checkout experiment-base

## Regeneración de TODO
```bash
python scripts/generate_todo.py
```

## Estructura de Logs
Los logs siguen formato markdown estructurado para fácil lectura y parsing.

## Emergency Reset
```bash
git checkout experiment-base
rm -rf logs/
./scripts/setup_logging.sh
```
