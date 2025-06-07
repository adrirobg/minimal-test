# Directivas Específicas de Tarea - PKM Frontend (PKM_FRONTEND_001)

## Información de la Tarea
- **ID de Tarea**: PKM_FRONTEND_001
- **Alcance**: Implementación completa del frontend PKM con React, Next.js, Tailwind CSS y ShadCN UI
- **Prioridad**: MÁXIMA - Estas directivas COMPLEMENTAN y TIENEN PRIORIDAD sobre las reglas generales

## DO'S (Buenas Prácticas Obligatorias)

### Arquitectura y Estructura
- **DO**: Seguir estrictamente la estructura de directorios definida en `development_guide.md`:
  ```
  frontend/
  ├── app/                 # Next.js App Router
  ├── components/         # Componentes reutilizables
  ├── lib/               # Utilidades y servicios
  └── types/             # Definiciones TypeScript
  ```

- **DO**: Usar componentes de ShadCN UI como base para todos los elementos de interfaz
- **DO**: Implementar tipado TypeScript estricto para todas las entidades y DTOs
- **DO**: Crear servicios API dedicados en `/lib/api/` siguiendo el patrón DTO del backend

### Autenticación y Seguridad
- **DO**: Implementar autenticación con NextAuth.js usando estrategia JWT
- **DO**: Usar cookies seguras para almacenar tokens (NO localStorage)
- **DO**: Implementar middleware de autenticación para rutas protegidas
- **DO**: Validar permisos en cada operación según roles de usuario

### Estado y Datos
- **DO**: Usar Zustand para estado global compartido entre componentes
- **DO**: Implementar persistencia de estado donde sea apropiado
- **DO**: Crear hooks personalizados para lógica de negocio compleja
- **DO**: Usar `axios.create` para crear instancia configurada con baseURL e interceptores

### UI/UX Específico PKM
- **DO**: Implementar TreeView con funcionalidad de colapsado/expansión para proyectos
- **DO**: Crear sistema de navegación jerárquica (Proyectos > Subproyectos > Notas)
- **DO**: Implementar búsqueda semántica con filtros múltiples
- **DO**: Crear editor de notas con soporte para enlaces entre notas

## DON'TS (Anti-Patrones Prohibidos)

### Arquitectura
- **DON'T**: Crear componentes sin seguir el sistema de diseño de ShadCN
- **DON'T**: Implementar lógica de negocio directamente en componentes de UI
- **DON'T**: Usar CSS personalizado cuando exista solución en Tailwind/ShadCN
- **DON'T**: Crear servicios sin tipado TypeScript estricto

### Seguridad
- **DON'T**: Almacenar información sensible en localStorage o sessionStorage
- **DON'T**: Hacer llamadas API sin validación de autenticación
- **DON'T**: Exponer tokens o credenciales en el código cliente
- **DON'T**: Implementar lógica de autorización solo en el frontend

### Datos y Estado
- **DON'T**: Hacer llamadas API directas desde componentes (usar servicios)
- **DON'T**: Sobrecargar el estado global con datos temporales
- **DON'T**: Crear múltiples instancias de Axios sin configuración centralizada
- **DON'T**: Ignorar manejo de errores en llamadas asíncronas

## GUIDELINES (Directrices Específicas)

### Configuración Técnica
- **GUIDELINE**: Configurar `axios.create` con:
  ```typescript
  const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
  });
  ```

- **GUIDELINE**: Estructura de servicios API siguiendo patrón:
  ```typescript
  // lib/api/[entity].service.ts
  export class EntityService {
    async getAll(): Promise<EntityListDTO> { }
    async getById(id: string): Promise<EntityDetailDTO> { }
    async create(data: EntityCreateDTO): Promise<EntityDetailDTO> { }
    // etc.
  }
  ```

### Componentes y UI
- **GUIDELINE**: Todos los formularios deben usar `react-hook-form` con validación Zod
- **GUIDELINE**: Implementar loading states y error boundaries en todos los componentes
- **GUIDELINE**: Usar `Suspense` para carga lazy de componentes pesados
- **GUIDELINE**: Implementar dark mode usando el sistema de temas de ShadCN

### Testing
- **GUIDELINE**: Escribir tests unitarios para hooks personalizados
- **GUIDELINE**: Implementar tests de integración para flujos completos
- **GUIDELINE**: Usar Playwright para tests E2E de funcionalidades críticas
- **GUIDELINE**: Mockear servicios API en tests unitarios

### Performance
- **GUIDELINE**: Implementar lazy loading para componentes no críticos
- **GUIDELINE**: Usar `useMemo` y `useCallback` apropiadamente
- **GUIDELINE**: Optimizar re-renders con `React.memo` donde aplique
- **GUIDELINE**: Implementar paginación en listas largas

## Context7 Libraries Requeridas

El Coder DEBE consultar estas librerías via Context7 antes de implementar:

1. **Next.js** (`/vercel/next.js`) - App Router, middleware, layouts
2. **React** (`/reactjs/react.dev`) - Hooks, componentes, estado
3. **Tailwind CSS** (`/tailwindlabs/tailwindcss.com`) - Responsive, dark mode
4. **ShadCN UI** (`/shadcn-ui/ui`) - Componentes, temas
5. **NextAuth.js** (`/nextauthjs/next-auth`) - JWT, sesiones
6. **Zustand** (`/pmndrs/zustand`) - Estado global
7. **Axios** (`/axios/axios-docs`) - HTTP client, interceptores

## Entregables Esperados

### Estructura Mínima Requerida
```
frontend/
├── app/
│   ├── (auth)/
│   ├── dashboard/
│   ├── projects/
│   ├── notes/
│   └── search/
├── components/
│   ├── ui/           # ShadCN components
│   ├── forms/
│   ├── navigation/
│   └── pkm/         # PKM-specific components
├── lib/
│   ├── api/         # API services
│   ├── auth/        # Auth configuration
│   ├── store/       # Zustand stores
│   └── utils/       # Utilidades
└── types/           # TypeScript definitions
```

### Funcionalidades Core
1. **Autenticación completa** con login/logout/registro
2. **Dashboard principal** con resumen de actividad
3. **Gestión de proyectos** con estructura jerárquica
4. **Editor de notas** con enlaces internos
5. **Sistema de búsqueda** semántica y por filtros
6. **Navegación responsive** con sidebar colapsable

## Validación Final

Antes de marcar la tarea como completada, verificar:
- [ ] Todos los Context7 IDs han sido consultados
- [ ] Estructura de archivos sigue la guía exactamente
- [ ] Autenticación JWT implementada y funcional
- [ ] Componentes ShadCN integrados correctamente
- [ ] Estado global Zustand configurado
- [ ] Servicios API con tipado estricto
- [ ] Tests básicos implementados
- [ ] Dark mode funcional
- [ ] Responsive design validado

## Notas Importantes

- Esta tarea es **CRÍTICA** para el proyecto PKM
- La calidad del código debe ser **PRODUCTION-READY**
- Seguir **EXACTAMENTE** los patrones definidos en `development_guide.md`
- Consultar Context7 **OBLIGATORIAMENTE** antes de implementar
- Documentar decisiones técnicas importantes