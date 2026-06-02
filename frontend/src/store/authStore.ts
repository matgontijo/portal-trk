// frontend/src/store/authStore.ts
// Store Zustand de autenticação do Portal TRK.
// Gerencia: user, token, login, logout, refresh silencioso.

import { create } from 'zustand'
import type { User } from '../types/auth'
import api from '../services/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email: string, password: string) => {
    // FastAPI OAuth2PasswordRequestForm exige form-urlencoded com campos 'username' e 'password'
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)

    // Buscar dados do usuário
    const meResponse = await api.get('/auth/me')
    set({ user: meResponse.data, isAuthenticated: true, isLoading: false })
  },

  logout: async () => {
    try {
      await api.post('/auth/logout')
    } catch {
      // Continua mesmo se falhar
    }
    localStorage.removeItem('access_token')
    set({ user: null, isAuthenticated: false, isLoading: false })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isLoading: false })
      return
    }

    try {
      const response = await api.get('/auth/me')
      set({ user: response.data, isAuthenticated: true, isLoading: false })
    } catch {
      localStorage.removeItem('access_token')
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  setUser: (user: User) => set({ user }),
}))
