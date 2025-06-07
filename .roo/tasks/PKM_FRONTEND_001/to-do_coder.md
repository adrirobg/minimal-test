# To-Do Coder: Implementación Frontend PKM (ID: PKM_FRONTEND_001)

## Fase 1: Configuración Inicial
- [ ] Crear proyecto Next.js con TypeScript, Tailwind y ESLint
- [ ] Configurar ShadCN UI (`npx shadcn-ui@latest init`)
- [ ] Configurar NextAuth.js para autenticación JWT
- [ ] Establecer store global con Zustand
- [ ] Configurar cliente API con Axios e interceptores

## Fase 2: Implementación de Componentes
### Componentes Principales
- [ ] `TreeView` jerárquico para proyectos/subproyectos
- [ ] `MarkdownEditor` con soporte para enlaces internos
- [ ] `CRUDForm` genérico para entidades (proyectos, notas)
- [ ] `SearchBar` con filtros semánticos

### Vistas
- [ ] Dashboard principal con resumen de proyectos
- [ ] Vista detalle de proyecto con árbol de subproyectos
- [ ] Editor de notas con preview en tiempo real
- [ ] Gestión de usuarios/perfiles

## Fase 3: Integración con API
- [ ] Implementar servicios API para cada entidad (DTOs)
- [ ] Conectar componentes a store global Zustand
- [ ] Manejar estados de carga/error en todas las vistas
- [ ] Implementar refresh token automático

## Fase 4: Pruebas y Validación
- [ ] Tests unitarios para componentes (Jest + RTL)
- [ ] Tests de integración para flujos completos
- [ ] Pruebas E2E con Playwright
- [ ] Validación de formularios con react-hook-form + Zod

## Fase 5: Documentación y Optimización
- [ ] Generar JSDoc/TSDoc para componentes clave
- [ ] Optimizar rendimiento con lazy loading
- [ ] Implementar dark mode responsive
- [ ] Documentar flujos de usuario básicos

## Recursos Obligatorios
- Directivas específicas: `.roo/rules-code/00_task_specific_directives_PKM_FRONTEND_001.md`
- Context7 Checklist: `.roo/tasks/PKM_FRONTEND_001/context7_checklist.md`
- Guía de desarrollo: `.roo/tasks/PKM_FRONTEND_001/development_guide.md`

## Criterios de Aceptación
- 100% de cobertura para componentes core
- 0 errores en ESLint y TypeScript
- Performance > 90 en Lighthouse
- WCAG 2.1 AA compliant