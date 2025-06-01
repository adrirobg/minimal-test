# Modelos ORM SQLAlchemy

Este submódulo define los modelos ORM de SQLAlchemy que representan las entidades principales del dominio PKM en la base de datos relacional. Cada clase modela una tabla y sus relaciones, siguiendo las convenciones y patrones de Clean Architecture.

## Entidades principales

- **UserProfile**: Perfil de usuario, raíz de la mayoría de relaciones.
- **Note**: Nota individual, enlazada a usuario, proyecto, fuente y keywords.
- **Project**: Organización jerárquica de notas.
- **Source**: Fuente de información asociada a notas.
- **Keyword**: Etiquetas para clasificar notas.
- **NoteLink**: Relación entre notas (enlaces semánticos).
- **Tablas de asociación**: Gestionan relaciones N:M (ej. nota-keyword).

## Características

- Uso de convenciones de nombres para constraints y migraciones.
- Relaciones explícitas entre entidades.
- Preparado para migraciones con Alembic.
- Facilita la evolución del esquema y la trazabilidad de datos.

## Relación con otros módulos

Estos modelos son utilizados por los repositorios de [`../repositories`](../repositories/README.md) para implementar el acceso a datos y por las unidades de trabajo para la gestión transaccional.
