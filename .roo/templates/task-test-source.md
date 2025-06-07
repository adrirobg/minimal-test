# Implementar Tests para Casos de Uso de la Entidad `source`

## Context

Esta tarea se enmarca dentro del desarrollo del backend para la aplicación de Gestión de Conocimiento Personal (PKM).  
Los casos de uso para la entidad `source` (CRUDL: Create, Get, List, Update, Delete) ya han sido implementados y se encuentran en `application/use_cases/source/`.

El objetivo de esta tarea es asegurar la calidad y robustez de dichos casos de uso mediante la creación de una suite de tests exhaustiva.  
Los nuevos tests deben seguir de cerca los patrones, la estructura y el nivel de cobertura de los tests ya existentes para la entidad `user_profile`, que servirán como principal referencia.

Se utilizará el stack tecnológico definido en el perfil del proyecto (`.roo/rules-code/01_project_profile_and_stack.md` o similar), incluyendo Python, Poetry, pytest para la ejecución de tests, y pre-commit para las validaciones de calidad.

---

## Scope

La tarea se centra en la creación e implementación de tests para cada uno de los casos de uso existentes de la entidad `source`.  
Asumiendo los casos de uso CRUDL, esto implicaría tests para:

- `CreateSourceUseCase`
- `GetSourceUseCase`
- `ListSourcesUseCase`
- `UpdateSourceUseCase`
- `DeleteSourceUseCase`

Para cada caso de uso de `source`:

1. **Análisis del Caso de Uso source:**  
   Comprender la lógica y el comportamiento del caso de uso de `source` ya implementado.

2. **Estudio de Tests de Referencia (user_profile):**  
   Analizar el archivo de test correspondiente de la entidad `user_profile` (ej. `test_create_user_profile_use_case.py` como guía para `test_create_source_use_case.py`) para entender la estructura, tipos de tests (unitarios, integración si aplica), uso de mocks/fixtures, y casos de prueba cubiertos.

3. **Implementación de Tests para source:**  
   Escribir los tests para el caso de uso de `source`, asegurando una cobertura adecuada de:
   - Caminos felices (happy paths).
   - Casos límite (edge cases).
   - Manejo de errores y excepciones esperadas.

4. **Validación de Tests:**  
   Ejecutar todos los tests para la entidad `source` (ej. `poetry run pytest tests/application/use_cases/source/`) y asegurar que el 100% de los tests pasan.  
   Confirmar que no se introducen regresiones en otras partes del sistema.

5. **Validación Pre-commit:**  
   Ejecutar `pre-commit run --all-files` sobre los nuevos archivos de test y cualquier archivo modificado.

6. **Re-validación de Tests (si aplica):**  
   Si pre-commit realiza modificaciones, volver a ejecutar todos los tests relevantes para `source` y confirmar que siguen pasando.

7. **Calidad del Código de Test:**  
   Asegurar que los tests son claros, legibles, mantenibles y bien comentados donde sea necesario.

---

## Expected Output

- **Archivos de Tests:**  
  Archivos Python con los tests para cada caso de uso de `source` (ej. `test_create_source_use_case.py`, `test_get_source_use_case.py`, etc.), ubicados en el directorio de tests apropiado (presumiblemente `tests/application/use_cases/source/`).

- **Confirmación de Tests Exitosos:**  
  Evidencia o confirmación de que la suite de tests relevante para `source` (`poetry run pytest tests/application/use_cases/source/` o la ruta específica) pasa sin errores y no introduce fallos en la suite global de tests del proyecto.

- **Confirmación de Validación Pre-commit:**  
  Evidencia o confirmación de que `pre-commit run --all-files` se ejecuta exitosamente en todos los archivos relevantes.

- **Código de Test de Calidad:**  
  Tests legibles, bien estructurados y con comentarios adecuados donde sea necesario.  
  Adherencia a los patrones de testing establecidos en el proyecto (basados en los tests de `user_profile`).

---

## Additional Resources

- **Referencia Principal para Patrones de Tests:**  
  Tests existentes de la entidad `user_profile`.  
  Ruta a los tests de `user_profile`: `tests/application/use_cases/user_profile/` (o la ruta correcta si es diferente).

- **Código Fuente de los Casos de Uso de source (ya implementados, para los que se crearán tests):**  
  Ruta al código: `application/use_cases/source/`

- **DTOs Relevantes para source (para entender la estructura de datos que manejan los casos de uso y que los tests deben simular/verificar):**  
  - `source_dto.py` (Ruta: `application/dtos/source_dto.py`)

- **Interfaces de Repositorio Relevantes para source (para crear mocks o stubs en los tests):**  
  - `source_interface.py` (Ruta: `application/interfaces/source_interface.py`)

- **Perfil del Proyecto y Stack Tecnológico:**  
  (El Coder lo tendrá en su system prompt)  
  `.roo/rules-code/01_project_profile_and_stack.md` (o el nombre y ruta final que hayamos establecido).

- **Directrices Generales de Código y Testing:**  
  (El Coder las tendrá en su system prompt)  
  `code_guidelines.md` (v3.3 o la versión más reciente).

- **Herramientas de Soporte:**  
  - `codebase_search`: Para explorar y entender el código existente de los casos de uso de `source` y los tests de `user_profile`.
  - `context7`: Para consultas sobre pytest, pytest-asyncio, o cualquier otra librería de testing si fuera necesario.

---

## Meta-Information

- `task_id`: [ORCHESTRATOR_WILL_ASSIGN_ID]
- `assigned_to`: PythonCoder (o el MODE que el Orchestrator determine como más adecuado para la creación de tests en Python, podría ser el mismo Coder que implementa la lógica)
- `priority`: HIGH
- `dependencies`:
  - Implementación completa y funcional de todos los casos de uso para la entidad `source` (Create, Get, List, Update, Delete).
  - Disponibilidad y estabilidad de los tests de la entidad `user_profile` como referencia clara y funcional.
  - Definición y disponibilidad de `SourceDTO` y `SourceRepositoryInterface` en el código base.