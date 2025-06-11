import { z } from 'zod';

// Authentication schemas
export const LoginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
});

export const RegisterSchema = z.object({
  name: z.string().min(1, 'El nombre es requerido'),
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword'],
});

// Authentication types
export type LoginCredentials = z.infer<typeof LoginSchema>;
export type RegisterData = z.infer<typeof RegisterSchema>;

// Session user interface
export interface SessionUser {
  id: string;
  name: string;
  email: string;
  image?: string;
}

// Auth response interfaces
export interface AuthResponse {
  user: SessionUser;
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface RefreshTokenResponse {
  accessToken: string;
  expiresAt: number;
}

// Auth state interface
export interface AuthState {
  user: SessionUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// NextAuth types extension (will be enabled when NextAuth is properly configured)
/*
declare module 'next-auth' {
  interface Session {
    user: SessionUser;
    accessToken: string;
  }

  interface User extends SessionUser {
    accessToken: string;
    refreshToken: string;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken: string;
    refreshToken: string;
    accessTokenExpires: number;
    user: SessionUser;
  }
}
*/
