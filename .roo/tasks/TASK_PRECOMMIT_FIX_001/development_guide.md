# Guía de Desarrollo: Corregir Validaciones Pre-Commit (TASK_PRECOMMIT_FIX_001)

## Objetivo
El objetivo de esta tarea es ejecutar las validaciones de pre-commit, analizar los errores reportados y corregirlos iterativamente hasta que todas las validaciones pasen exitosamente.

## Referencias Clave
- Archivo de configuración de pre-commit: [`./.pre-commit-config.yaml`](./.pre-commit-config.yaml)
- Archivo para agrupar errores: [`./.roo/tasks/TASK_PRECOMMIT_FIX_001/pre-commit-errors.md`](./.roo/tasks/TASK_PRECOMMIT_FIX_001/pre-commit-errors.md) (Este archivo debe ser creado y utilizado por el Coder).

## Procedimiento
1.  Ejecutar `pre-commit run --all-files`.
2.  Analizar la salida de consola para identificar los errores.
3.  Agrupar los errores en el archivo [`./.roo/tasks/TASK_PRECOMMIT_FIX_001/pre-commit-errors.md`](./.roo/tasks/TASK_PRECOMMIT_FIX_001/pre-commit-errors.md).
4.  Utilizar las herramientas de Context7 (`resolve-library-id`, `get-library-docs`) para buscar documentación y ejemplos sobre cómo corregir los errores identificados.
5.  Aplicar las correcciones necesarias en los archivos afectados.
6.  Repetir los pasos 1-5 hasta que `pre-commit run --all-files` no reporte errores.

## Patrones y Consideraciones
- Prestar atención a los mensajes de error específicos de cada hook de pre-commit.
- Priorizar la corrección de errores que se repiten en múltiples archivos.
- Utilizar la documentación de las librerías (obtenida vía Context7) para entender la causa raíz de los problemas y la forma correcta de solucionarlos.
- Asegurar que las correcciones no introduzcan nuevos errores o regresiones.
