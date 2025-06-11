# To-Do Coder: Implementación de Datos de Prueba PKM (ID: PKM_TEST_DATA_001)
Progreso General Coder: 15/19 checks

## Fase 1: Generación de Scripts Python para Datos de Prueba
- [X] Crear el directorio `/src/pkm_app/tests/data_generation/`.
- [X] Crear `generate_test_data.py` en `/src/pkm_app/tests/data_generation/`.
- [X] Crear scripts entidad-específicos (ej. `users_data.py`, `projects_data.py`, `notes_data.py`, `sources_data.py`, `keywords_data.py`, `note_links_data.py`) en `/src/pkm_app/tests/data_generation/`.
- [X] Implementar la lógica de generación de datos en los scripts Python, siguiendo las cantidades y relaciones especificadas en la `development_guide.md`.
- [X] Asegurar que los datos generados cumplan con los DTOs/esquemas Pydantic y los modelos de dominio.
- [X] Incluir comentarios explicativos en los scripts.

## Fase 2: Creación de Migración Alembic y Archivo de Semilla SQL
- [X] Generar un nuevo archivo de migración Alembic en `/src/pkm_app/infrastructure/persistence/migrations/versions/`.
- [X] Implementar la lógica de inserción de datos en la migración Alembic, utilizando SQL directamente.
- [X] Crear el archivo de semilla SQL `seed.sql` en `/src/pkm_app/infrastructure/persistence/schema/`.
- [X] Asegurar que la migración sea reproducible y consistente.

## Fase 3: Documentación
- [X] Crear `TEST_DATA_README.md` en `/src/pkm_app/tests/`.
- [X] Documentar la estructura de los datos generados en `TEST_DATA_README.md`.
- [X] Incluir instrucciones para la ejecución de la migración y la generación de datos en `TEST_DATA_README.md`.
- [X] Añadir ejemplos de datos y un diagrama de relaciones entre entidades en `TEST_DATA_README.md`.

## Fase 4: Verificación y Validación
- [ ] Ejecutar la migración para poblar la base de datos de prueba.
- [ ] Validar que los datos insertados cumplen con los criterios de calidad (cobertura de casos, realismo simplificado).
- [ ] Verificar que las relaciones entre entidades son válidas.
- [ ] Confirmar que el sistema puede ser debuggeado visualmente con los datos generados.