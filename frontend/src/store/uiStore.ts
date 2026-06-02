// frontend/src/store/uiStore.ts
// Store Zustand de estado UI do Portal TRK.
// Gerencia: tema (claro/escuro), sidebar, mobile nav.

import { create } from 'zustand'

interface UIState {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  mobileNavVisible: boolean
  toggleTheme: () => void
  setSidebarOpen: (open: boolean) => void
  setMobileNavVisible: (visible: boolean) => void
}

export const useUIStore = create<UIState>((set) => ({
  theme: (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches)
    ? 'dark' : 'light',
  sidebarOpen: true,
  mobileNavVisible: false,

  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light'
    // Atualizar classe no documentElement
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', newTheme === 'dark')
    }
    return { theme: newTheme }
  }),

  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
  setMobileNavVisible: (visible: boolean) => set({ mobileNavVisible: visible }),
}))
