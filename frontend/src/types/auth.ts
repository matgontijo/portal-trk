// frontend/src/types/auth.ts
// Tipos de autenticação do Portal TRK

export type UserRole = 'admin' | 'gestor' | 'funcionario'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  is_active: boolean
  phone_whatsapp: string | null
  avatar_url: string | null
  sector: string | null
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserBrief {
  id: string
  name: string
  role: string
  avatar_url: string | null
}
