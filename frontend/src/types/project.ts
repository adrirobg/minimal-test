import { z } from 'zod';

// Base schema for project validation
export const ProjectBaseSchema = z.object({
  name: z.string().min(1, 'El nombre del proyecto es requerido'),
  description: z.string().optional(),
  parent_project_id: z.string().uuid().optional(),
});

// Schema for creating a new project
export const ProjectCreateSchema = ProjectBaseSchema;

// Schema for updating a project
export const ProjectUpdateSchema = z.object({
  name: z.string().min(1).optional(),
  description: z.string().optional(),
  parent_project_id: z.string().uuid().optional(),
});

// Complete project interface (from API response)
export interface Project {
  id: string;
  name: string;
  description?: string;
  parent_project_id?: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Types derived from schemas
export type ProjectCreate = z.infer<typeof ProjectCreateSchema>;
export type ProjectUpdate = z.infer<typeof ProjectUpdateSchema>;

// Project with hierarchical structure for TreeView
export interface ProjectNode extends Project {
  children?: ProjectNode[];
  parent?: ProjectNode;
}

// Project list response
export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page?: number;
  limit?: number;
}
