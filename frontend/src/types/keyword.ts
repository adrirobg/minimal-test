import { z } from 'zod';

// Base schema for keyword validation
export const KeywordBaseSchema = z.object({
  name: z.string().min(1, 'El nombre de la keyword es requerido'),
});

// Schema for creating a new keyword
export const KeywordCreateSchema = KeywordBaseSchema;

// Schema for updating a keyword
export const KeywordUpdateSchema = z.object({
  name: z.string().min(1).optional(),
});

// Complete keyword interface (from API response)
export interface Keyword {
  id: string;
  name: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Types derived from schemas
export type KeywordCreate = z.infer<typeof KeywordCreateSchema>;
export type KeywordUpdate = z.infer<typeof KeywordUpdateSchema>;

// Keyword list response
export interface KeywordListResponse {
  keywords: Keyword[];
  total: number;
  page?: number;
  limit?: number;
}
