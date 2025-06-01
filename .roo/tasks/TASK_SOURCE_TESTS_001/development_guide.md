# Guía de Desarrollo para Tests de Source

## Objetivo
Implementar tests unitarios para los casos de uso CRUDL de la entidad Source:
- CreateSourceUseCase
- GetSourceUseCase
- ListSourcesUseCase
- UpdateSourceUseCase
- DeleteSourceUseCase

## Referencias Clave
- **Tests de Note**: `src/pkm_app/tests/unit/core/application/use_cases/note/`
- **Casos de Uso Source**: `src/pkm_app/core/application/use_cases/source/`
- **DTOs**: `src/pkm_app/core/application/dtos/source_dto.py`
- **Interfaces**: `src/pkm_app/core/application/interfaces/source_interface.py`

## Patrones a Seguir
1. Estructura similar a los tests de note
2. Uso de fixtures y mocks para el repositorio (ejemplo):
```python
@pytest.fixture
def mock_uow():
    uow = AsyncMock(UnitOfWorkInterface)
    uow.__aenter__.return_value = uow
    return uow
```
3. Cobertura de:
   - Happy paths
   - Casos límite
   - Manejo de errores
4. Validación con pytest y pre-commit
5. Checklist de casos por cada caso de uso:
   - Creación exitosa
   - Validación de entrada
   - Manejo de errores
   - Permisos de usuario

## Entregables Esperados
- `test_create_source_use_case.py`
- `test_get_source_use_case.py`
- `test_list_sources_use_case.py`
- `test_update_source_use_case.py`
- `test_delete_source_use_case.py`
