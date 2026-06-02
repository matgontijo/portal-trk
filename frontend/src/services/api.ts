// frontend/src/services/api.ts
// Instância Axios do Portal TRK com interceptors.
// Responsabilidades:
//   - Base URL configurável
//   - Injetar Authorization header em todas as requisições
//   - Refresh automático: intercepta 401, renova token, retenta request
//   - Tratamento de erros global

import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
if (!API_URL.endsWith('/api/v1')) {
  // Se o usuário esqueceu de colocar o /api/v1 na variável do Render, a gente coloca por ele
  API_URL = `${API_URL.replace(/\/$/, '')}/api/v1`
}

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  withCredentials: true, // Envia cookies (refresh_token)
  headers: {
    'Content-Type': 'application/json',
  },
})

// Rotas de auth que NÃO devem disparar refresh automático
const AUTH_ROUTES = ['/auth/login', '/auth/refresh', '/auth/me', '/auth/logout']

// ─── Request Interceptor: injetar token ───
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ─── Response Interceptor: refresh automático ───
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const requestUrl = originalRequest?.url || ''

    // Não tentar refresh para rotas de auth (evita loop infinito)
    const isAuthRoute = AUTH_ROUTES.some(route => requestUrl.includes(route))

    // Se não é 401, já tentou retry, ou é rota de auth → rejeitar direto
    if (error.response?.status !== 401 || originalRequest._retry || isAuthRoute) {
      return Promise.reject(error)
    }

    // Se já está renovando, enfileirar esta requisição
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`
          }
          return api(originalRequest)
        })
        .catch((err) => Promise.reject(err))
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      // Chamar refresh (cookie httpOnly é enviado automaticamente)
      const response = await api.post('/auth/refresh')
      const { access_token } = response.data

      // Salvar novo token
      localStorage.setItem('access_token', access_token)

      // Atualizar header da requisição original
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${access_token}`
      }

      // Processar fila de requisições pendentes
      processQueue(null, access_token)

      // Retentar requisição original
      return api(originalRequest)
    } catch (refreshError) {
      // Refresh falhou — limpar tudo (NÃO redirecionar com window.location para evitar loop)
      processQueue(refreshError as AxiosError)
      localStorage.removeItem('access_token')
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default api
