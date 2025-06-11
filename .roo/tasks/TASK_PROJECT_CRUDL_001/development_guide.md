# Guía de Desarrollo: Casos de Uso CRUDL para la Entidad `project`

## Objetivo

Implementar los casos de uso principales (Crear, Leer, Listar, Actualizar, Borrar) para la entidad `project` en la capa de aplicación, siguiendo los patrones y estándares de calidad definidos en el proyecto y tomando como referencia la implementación madura de `user_profile`.

## Estructura y Patrones

- **Ubicación del código:**
  - Casos de uso: `src/pkm_app/core/application/use_cases/project/`
  - Tests: `src/pkm_app/tests/unit/core/application/use_cases/project/`
- **Referencia principal:**
  - Casos de uso de `user_profile`:
    - Código: `src/pkm_app/core/application/use_cases/user_profile/`
    - Tests: `src/pkm_app/tests/unit/core/application/use_cases/user_profile/`
- **Referencia secundaria:**
  - Casos de uso de `note`:
    - Código: `src/pkm_app/core/application/use_cases/note/`

## Componentes Clave

- **DTO:**
  - [`project_dto.py`](src/pkm_app/core/application/dtos/project_dto.py)
- **Interfaz de Repositorio:**
  - [`project_interface.py`](src/pkm_app/core/application/interfaces/project_interface.py)
- **Repositorio SQLAlchemy:**
  - [`project_repository.py`](src/pkm_app/infrastructure/persistence/sqlalchemy/repositories/project_repository.py)

## Estándares de Implementación

- **Patrón de casos de uso:**
  - Seguir la estructura de clases, métodos y logging de los casos de uso de `user_profile`.
  - Utilizar DTOs para entrada/salida.
  - Inyectar dependencias vía constructor.
- **Logging:**
  - Usar el sistema de logging centralizado del proyecto.
  - Incluir logs informativos en puntos clave (inicio, éxito, error).
- **Testing:**
  - Crear tests unitarios para cada caso de uso.
  - Ubicar los tests en el directorio correspondiente.
  - Seguir la estructura y cobertura de los tests de `user_profile`.
- **Documentación:**
  - Incluir docstrings claros en clases y métodos.
- **Calidad:**
  - Cumplir con las reglas de pre-commit y los linters definidos en el proyecto.
  - Mantener el código bajo 500 líneas por archivo.

## DTOs y Repositorios

- **DTO principal:**
  - `ProjectDTO`
- **Interfaz:**
  - `ProjectRepositoryInterface`

## Ejemplo de Estructura de un Caso de Uso

```python
class CreateProjectUseCase:
    def __init__(self, repository: ProjectRepositoryInterface):
        self.repository = repository

    def execute(self, dto: ProjectDTO) -> ProjectDTO:
        # Logging de inicio
        # Lógica de creación
        # Logging de éxito/error
        return created_project_dto
```

## Referencias de Código

- [`create_user_profile_use_case.py`](src/pkm_app/core/application/use_cases/user_profile/create_user_profile_use_case.py)
- [`test_create_user_profile_use_case.py`](src/pkm_app/tests/unit/core/application/use_cases/user_profile/test_create_user_profile_use_case.py)

## Validaciones

- Ejecutar `poetry run pytest src/pkm_app/tests/unit/core/application/use_cases/project/`
- Ejecutar `pre-commit run --all-files`

## Notas

- No hardcodear valores sensibles.
- Mantener consistencia en nombres y estructura.
- Actualizar el to-do y el estado de la tarea tras cada fase.
