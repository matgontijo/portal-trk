import { create } from 'zustand'
import api from '../api'
import type { Sessao, Usuario, PermMap } from '../types'

interface AuthState {
  usuario: Usuario | null
  permissoes: PermMap
  modulos: string[]
  carregando: boolean
  entrar: (email: string, senha: string) => Promise<void>
  sair: () => void
  carregar: () => Promise<void>
  pode: (modulo: string, acao?: 'ver' | 'editar') => boolean
}

export const useAuth = create<AuthState>((set, get) => ({
  usuario: null,
  permissoes: {},
  modulos: [],
  carregando: true,

  entrar: async (email, senha) => {
    const { data } = await api.post<Sessao>('/auth/login', { email, senha })
    localStorage.setItem('trk_token', data.token)
    set({ usuario: data.usuario, permissoes: data.permissoes, modulos: data.modulos_acessiveis, carregando: false })
  },

  sair: () => {
    localStorage.removeItem('trk_token')
    set({ usuario: null, permissoes: {}, modulos: [] })
  },

  carregar: async () => {
    const token = localStorage.getItem('trk_token')
    if (!token) { set({ carregando: false }); return }
    try {
      const { data } = await api.get('/auth/me')
      set({ usuario: data.usuario, permissoes: data.permissoes, modulos: data.modulos_acessiveis, carregando: false })
    } catch {
      localStorage.removeItem('trk_token')
      set({ usuario: null, carregando: false })
    }
  },

  pode: (modulo, acao = 'ver') => {
    const { usuario, permissoes } = get()
    if (usuario?.cargo === 'diretor') return true
    return !!permissoes[modulo]?.[acao]
  },
}))
