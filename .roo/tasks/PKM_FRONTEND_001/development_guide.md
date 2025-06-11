# Guía de Desarrollo Frontend PKM

## Configuración Inicial
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint
cd frontend
npm install @shadcn/ui
npx shadcn-ui@latest init
```

## Estructura de Directorios
```
frontend/
├── app/
│   ├── (auth)/
│   ├── (main)/
│   ├── api/
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/  # Componentes ShadCN
│   ├── projects/
│   ├── notes/
│   └── shared/
├── lib/
│   ├── api/  # Clients API
│   └── stores/ # Zustand stores
├── types/
└── public/
```

## Consumo de API
```typescript
// Ejemplo de client API para proyectos
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: { Authorization: `Bearer ${token}` }
});

export const getProjects = async () => {
  const response = await apiClient.get('/projects');
  return response.data;
};
```

## Componentes Clave
1. **TreeView**: Componente jerárquico para proyectos/subproyectos
2. **MarkdownEditor**: Editor de notas con soporte Markdown
3. **CRUDForm**: Formularios reutilizables para entidades

## Pruebas
```bash
npm install -D @playwright/test
npx playwright install
```

## Recursos
- [Documentación ShadCN](https://ui.shadcn.com)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Zustand Docs](https://zustand-demo.pmnd.rs)