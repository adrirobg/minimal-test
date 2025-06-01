# Guía de Desarrollo: Casos de Uso `keyword` (CRUDL)

## Objetivo
Implementar los casos de uso principales para la entidad `keyword` siguiendo los patrones y estándares de los casos de uso de `user_profile` y `note`.

## Referencias Clave
- Casos de uso `user_profile`: [`src/pkm_app/core/application/use_cases/user_profile/`](src/pkm_app/core/application/use_cases/user_profile/)
- Casos de uso `note`: [`src/pkm_app/core/application/use_cases/note/`](src/pkm_app/core/application/use_cases/note/)
- DTO: [`src/pkm_app/core/application/dtos/keyword_dto.py`](src/pkm_app/core/application/dtos/keyword_dto.py)
- Interfaz repositorio: [`src/pkm_app/core/application/interfaces/keyword_interface.py`](src/pkm_app/core/application/interfaces/keyword_interface.py)

## Stack y Herramientas
- Python + Poetry
- Pre-commit
- Tests unitarios/integración

## Patrones y Consideraciones
- Seguir estructura, logging y comentarios de los casos de uso de `user_profile`.
- Implementar docstrings claros en clases y métodos.
- Tests exhaustivos, cubriendo casos principales y bordes.
- Validar con `poetry run test` y `pre-commit run --all-files`.
- Si pre-commit modifica archivos, volver a ejecutar tests.
- Mantener código modular y limpio.

## Estructura Esperada
- Código: `src/pkm_app/core/application/use_cases/keyword/`
- Tests: `src/pkm_app/tests/unit/core/application/use_cases/test_keyword/`
- DTO: `src/pkm_app/core/application/dtos/keyword_dto.py`
- Interfaz: `src/pkm_app/core/application/interfaces/keyword_interface.py`

## Ejemplo de flujo
1. Implementar caso de uso (ej. `CreateKeywordUseCase`).
2. Escribir tests.
3. Ejecutar tests y pre-commit.
4. Documentar con docstrings.
5. Validar calidad y cobertura.

## Recursos útiles
- [Patrones de logging Python](https://docs.python.org/3/howto/logging.html)
- [Documentación Poetry](https://python-poetry.org/docs/)
- [Pre-commit](https://pre-commit.com/)