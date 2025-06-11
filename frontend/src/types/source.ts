import { z } from 'zod';

// Base schema for source validation
export const SourceBaseSchema = z.object({
  name: z.string().min(1, 'El nombre de la fuente es requerido'),
  type: z.string().max(100).optional(),
  url: z.string().url().optional(),
  description: z.string().optional(),
  source_metadata: z.record(z.unknown()).optional(),
});

// Schema for creating a new source
export const SourceCreateSchema = SourceBaseSchema;

// Schema for updating a source
export const SourceUpdateSchema = z.object({
  name: z.string().min(1).optional(),
  type: z.string().max(100).optional(),
  url: z.string().url().optional(),
  description: z.string().optional(),
  source_metadata: z.record(z.unknown()).optional(),
});

// Complete source interface (from API response)
export interface Source {
  id: string;
  name: string;
  type?: string;
  url?: string;
  description?: string;
  source_metadata?: Record<string, unknown>;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Types derived from schemas
export type SourceCreate = z.infer<typeof SourceCreateSchema>;
export type SourceUpdate = z.infer<typeof SourceUpdateSchema>;

// Source list response
export interface SourceListResponse {
  sources: Source[];
  total: number;
  page?: number;
  limit?: number;
}
