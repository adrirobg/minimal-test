import { z } from 'zod';

// Base schema for user validation
export const UserProfileBaseSchema = z.object({
  name: z.string().min(1, 'El nombre es requerido'),
  email: z.string().email('Email inválido'),
  bio: z.string().optional(),
  settings: z.record(z.unknown()).optional(),
});

// Schema for creating a new user profile
export const UserProfileCreateSchema = UserProfileBaseSchema;

// Schema for updating a user profile
export const UserProfileUpdateSchema = z.object({
  name: z.string().min(1).optional(),
  email: z.string().email().optional(),
  bio: z.string().optional(),
  settings: z.record(z.unknown()).optional(),
});

// Complete user profile interface (from API response)
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  bio?: string;
  settings?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

// Types derived from schemas
export type UserProfileCreate = z.infer<typeof UserProfileCreateSchema>;
export type UserProfileUpdate = z.infer<typeof UserProfileUpdateSchema>;

// User list response
export interface UserListResponse {
  users: UserProfile[];
  total: number;
  page?: number;
  limit?: number;
}
