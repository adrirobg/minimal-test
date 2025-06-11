# Repositorios SQLAlchemy

Este submódulo implementa los repositorios concretos para cada entidad principal del sistema PKM, siguiendo las interfaces (puertos) definidas en la capa de aplicación. Los repositorios encapsulan la lógica de acceso a datos usando SQLAlchemy y gestionan la persistencia de manera desacoplada.

## Responsabilidades

- Implementar operaciones CRUD y consultas especializadas para:
  - Notas (`Note`)
  - Enlaces entre notas (`NoteLink`)
  - Proyectos (`Project`)
  - Fuentes (`Source`)
  - Keywords (`Keyword`)
  - Perfiles de usuario (`UserProfile`)
- Integrarse con el patrón Unit of Work para garantizar la atomicidad y consistencia de las transacciones.
- Soportar asincronía para entornos web y scripts, según el contexto de uso.

## Características

- Cada repositorio implementa una interfaz definida en `core/application/interfaces`.
- Permite cambiar la tecnología de persistencia sin afectar la lógica de negocio.
- Facilita pruebas unitarias y de integración mediante inyección de dependencias.

## Relación con otros módulos

Estos repositorios son utilizados por las unidades de trabajo y los casos de uso de la aplicación para acceder y modificar los datos del sistema, manteniendo la separación entre dominio y detalles de infraestructura.
