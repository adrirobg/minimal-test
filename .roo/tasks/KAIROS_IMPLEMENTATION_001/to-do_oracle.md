# To-Do Oráculo: KAIROS_IMPLEMENTATION_001

## Configuración Inicial (Pre-Fase 1)
- [ ] backend_setup: Configuración inicial del backend
- [ ] agno_setup: Instalación de Agno Framework

## Fase 1: MVP del Agente
- [ ] Configuración Agno + Gemini: Implementar integración básica con API Gemini (depende: agno_setup)
- [ ] Endpoint /chat básico: Crear endpoint inicial para interacción con el agente (depende: backend_setup)

## Fase 2: Persistencia y Herramientas
- [ ] Migración a PostgreSQL: Configurar persistencia de sesiones en PostgreSQL
- [ ] Herramienta RAG básica: Implementar búsqueda semántica sobre notas

## Fase 3: Optimización y Escalabilidad
- [ ] Arquitectura basada en eventos: Implementar patrones de mensajería para escalabilidad
- [ ] Mecanismos de robustez: Añadir circuit breakers y retry policies