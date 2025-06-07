import { z } from 'zod';
import { Project } from './project';
import { Source } from './source';
import { Keyword } from './keyword';

// Base schema for note validation
export const NoteBaseSchema = z.object({
  title: z.string().optional(),
  content: z.string().min(1, 'El contenido de la nota es requerido'),
  type: z.string().max(100).optional(),
  note_metadata: z.record(z.unknown()).optional(),
  project_id: z.string().uuid().optional(),
  source_id: z.string().uuid().optional(),
});

// Schema for creating a new note
export const NoteCreateSchema = NoteBaseSchema.extend({
  keywords: z.array(z.string()).optional(),
});

// Schema for updating a note
export const NoteUpdateSchema = z.object({
  title: z.string().optional(),
  content: z.string().optional(),
  type: z.string().max(100).optional(),
  note_metadata: z.record(z.unknown()).optional(),
  project_id: z.string().uuid().optional(),
  source_id: z.string().uuid().optional(),
  keywords: z.array(z.string()).optional(),
});

// Complete note interface (from API response)
export interface Note {
  id: string;
  title?: string;
  content: string;
  type?: string;
  note_metadata?: Record<string, unknown>;
  project_id?: string;
  source_id?: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  project?: Project;
  source?: Source;
  keywords: Keyword[];
}

// Note with links for detailed view
export interface NoteWithLinks extends Note {
  source_of_links: NoteLink[];
  target_of_links: NoteLink[];
}

// Note link interface
export interface NoteLink {
  id: string;
  source_note_id: string;
  target_note_id: string;
  link_type?: string;
  created_at: string;
  source_note?: Note;
  target_note?: Note;
}

// Types derived from schemas
export type NoteCreate = z.infer<typeof NoteCreateSchema>;
export type NoteUpdate = z.infer<typeof NoteUpdateSchema>;

// Note list response
export interface NoteListResponse {
  notes: Note[];
  total: number;
  page?: number;
  limit?: number;
}

// Search filters for notes
export interface NoteSearchFilters {
  query?: string;
  project_id?: string;
  type?: string;
  keywords?: string[];
  date_from?: string;
  date_to?: string;
}
