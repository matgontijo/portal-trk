import axios from 'axios'

// Dev: usa o proxy do Vite (/api). Produção: VITE_API_URL aponta para a API.
const baseURL = import.meta.env.VITE_API_URL || '/api'
const api = axios.create({ baseURL, timeout: 20000 })

api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('trk_token')
  if (token && cfg.headers) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('trk_token')
      if (location.pathname !== '/login') location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api
