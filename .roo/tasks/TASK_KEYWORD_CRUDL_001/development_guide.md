# Guía de Desarrollo: Casos de Uso CRUDL para la Entidad `keyword`

## Objetivo

Implementar los casos de uso principales (Crear, Leer, Listar, Actualizar, Borrar) para la entidad `keyword` siguiendo los patrones de diseño, estructura, logging y testing establecidos en los casos de uso de `user_profile` y `note`.

## Referencias Clave

- Casos de uso de `user_profile`: [`src/pkm_app/core/application/use_cases/user_profile/`](src/pkm_app/core/application/use_cases/user_profile/)
- Casos de uso de `note`: [`src/pkm_app/core/application/use_cases/note/`](src/pkm_app/core/application/use_cases/note/)
- DTO relevante: [`keyword_dto.py`](src/pkm_app/core/application/dtos/keyword_dto.py)
- Interfaz de repositorio: [`keyword_interface.py`](src/pkm_app/core/application/interfaces/keyword_interface.py)

## Estructura Recomendada

- Cada caso de uso debe estar en un archivo independiente bajo `src/pkm_app/core/application/use_cases/keyword/`.
- Los tests deben ubicarse en `src/pkm_app/tests/unit/core/application/use_cases/test_keyword/`.

## Patrones y Buenas Prácticas

- **Inyección de dependencias:** Recibe el repositorio y el UnitOfWork como argumentos.
- **DTOs:** Utiliza `KeywordDTO` para entrada/salida.
- **Logging:** Usa el logger del proyecto para registrar eventos clave y errores.
- **Errores:** Maneja errores usando excepciones definidas en `src/pkm_app/core/domain/errors.py`.
- **Comentarios y Docstrings:** Incluye docstrings claros en clases y métodos.
- **Tests:** Cubre casos principales, bordes y errores. Usa mocks para dependencias externas.

## Ejemplo de Firma de Caso de Uso

```python
class CreateKeywordUseCase:
    def __init__(self, repository: KeywordRepositoryInterface, uow: UnitOfWorkInterface):
        ...

    def execute(self, dto: KeywordDTO) -> KeywordDTO:
        """
        Crea una nueva keyword.
        """
        ...
```

## DTO y Repositorio

- [`KeywordDTO`](src/pkm_app/core/application/dtos/keyword_dto.py)
- [`KeywordRepositoryInterface`](src/pkm_app/core/application/interfaces/keyword_interface.py)

## Validación y Calidad

- Ejecutar `poetry run test` y asegurar 100% de tests pasan.
- Ejecutar `pre-commit run --all-files` y corregir cualquier issue.
- Repetir tests si pre-commit modifica archivos.

## Notas Finales

- Mantener los archivos bajo 500 líneas.
- No hardcodear valores de entorno ni secretos.
- Seguir la estructura y convenciones del proyecto.
