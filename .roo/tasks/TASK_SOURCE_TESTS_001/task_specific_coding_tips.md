# Task-Specific Coding Tips & Directives for: Implementación de Tests para Casos de Uso de Source

## Context7 Library Documentation to Review by Coder
**(Coder: Como primer paso, para cada librería listada abajo, usa su ID con la herramienta `get-library-docs` de `Context7` para obtener y revisar su documentación actualizada. Marca `[X]` después de hacerlo para cada una.)**
- [ ] `pytest` (`/pytest-dev/pytest`) (Sugerencia de `topic`: "async testing")

## DOs (Specific Best Practices for this Task)
- DO: Usar fixtures de pytest para mockear UnitOfWork y repositorios (ver `mock_uow_instance` en tests de Note)
- DO: Implementar tests asíncronos con `@pytest.mark.asyncio`
- DO: Cubrir happy paths, casos límite y manejo de errores en cada caso de uso
- DO: Validar permisos (user_id) y datos de entrada en cada test
- DO: Usar AsyncMock para mockear llamadas asíncronas
- DO: Verificar llamadas a commit/rollback en tests de operaciones que modifican datos

## DON'Ts (Specific Pitfalls to Avoid for this Task)
- DON'T: Olvidar mockear el comportamiento de __aenter__ en UnitOfWork
- DON'T: Implementar tests sincrónicos para código asíncrono
- DON'T: Dejar de probar casos de error y validación
- DON'T: Hardcodear valores que deberían ser generados (usar uuid.uuid4() para IDs)
- DON'T: Olvidar verificar llamadas a métodos mockeados (assert_called_once, etc.)

## Specific Library/API Usage Guidelines (if any for this task)
- GUIDELINE: Para pytest, seguir la estructura de fixtures mostrada en los tests de Note
- GUIDELINE: Usar pytest.raises para verificar excepciones esperadas

---
## Suggestions for `development_guide.md` (Optional - for Orchestrator's consideration)
- SUGGESTION: Añadir ejemplo concreto de fixture para mockear UnitOfWork
- SUGGESTION: Incluir checklist de casos de prueba a cubrir para cada caso de uso
