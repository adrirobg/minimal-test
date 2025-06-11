# Guía de Desarrollo: Casos de Uso CRUDL para `keyword`

## Objetivo Principal
Implementar los casos de uso CRUDL para la entidad `keyword` siguiendo los patrones y estándares de los casos de uso de `user_profile` y `note`.

## Referencias Clave
- Casos de uso de referencia:
  - [`user_profile`](src/pkm_app/core/application/use_cases/user_profile/)
  - [`note`](src/pkm_app/core/application/use_cases/note/)
- DTO relevante: [`keyword_dto.py`](src/pkm_app/core/application/dtos/keyword_dto.py)
- Interfaz de repositorio: [`keyword_interface.py`](src/pkm_app/core/application/interfaces/keyword_interface.py)

## Patrones y Consideraciones
- Seguir la estructura, logging y manejo de errores de los casos de uso de `user_profile`.
- Utilizar los DTOs y la interfaz de repositorio definidos.
- Incluir docstrings claros en clases y métodos.
- Añadir logging informativo en puntos clave (inicio, éxito, error).
- Mantener la cobertura de tests y calidad de código según pre-commit.

## Ciclo de Desarrollo
1. Implementar la lógica de cada caso de uso.
2. Crear tests unitarios/integración exhaustivos.
3. Ejecutar `poetry run test` y asegurar que todos los tests pasan.
4. Ejecutar `pre-commit run --all-files` y corregir cualquier issue.
5. Re-ejecutar tests si pre-commit modifica archivos.
6. Documentar el código y actualizar el checklist.

## Recursos Útiles
- [Patrones de casos de uso de user_profile](src/pkm_app/core/application/use_cases/user_profile/)
- [Patrones de casos de uso de note](src/pkm_app/core/application/use_cases/note/)
- [Tests de user_profile](src/pkm_app/tests/unit/core/application/use_cases/user_profile/)
- [Tests de note](src/pkm_app/tests/unit/core/application/use_cases/note/)
- [Tests de keyword](src/pkm_app/tests/unit/core/application/use_cases/test_keyword/)

## Enlaces Externos
- [Documentación Poetry](https://python-poetry.org/docs/)
- [Documentación pre-commit](https://pre-commit.com/)
