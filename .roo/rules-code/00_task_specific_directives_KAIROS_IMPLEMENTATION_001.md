# Directivas Específicas - KAIROS_IMPLEMENTATION_001

## Do's
✅ **Implementación de Agente**
- Usar Agno Framework con tipado estático
- Implementar todos los métodos como async
- Separar claramente dominio/aplicación/infraestructura
- Versionar prompts y configuración

✅ **Persistencia**
- Usar SQLAlchemy async para PostgreSQL
- Implementar modelos separados para memoria/sesión
- Validar todas las entradas de usuario

✅ **Herramientas RAG**
- Cachear resultados de búsquedas frecuentes
- Usar embeddings para búsqueda semántica
- Limitar contexto a notas del usuario actual

✅ **Escalabilidad**
- Diseñar para horizontal scaling desde inicio
- Usar particionamiento por usuario
- Implementar circuit breakers para APIs externas

## Don'ts
❌ **Implementación de Agente**
- Evitar acoplamiento con implementaciones específicas
- No exponer credenciales en logs
- No asumir estado entre reinicios

❌ **Persistencia**
- Evitar consultas sincrónicas
- No almacenar contexto completo en DB
- No mezclar modelos de agente con PKM

❌ **Herramientas RAG**
- No procesar datos sin validación
- Evitar búsquedas sin límites
- No cachear información sensible

❌ **Escalabilidad**
- No hardcodear configuraciones
- Evitar estado compartido entre instancias
- No asumir latencias fijas en APIs externas