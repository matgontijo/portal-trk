import axios from 'axios'

// Serviço único: o backend serve o frontend => '/api' relativo (mesma origem).
// Se VITE_API_URL vier setado, garante que termine em '/api'.
let baseURL = import.meta.env.VITE_API_URL || '/api'
if (!baseURL.endsWith('/api')) baseURL = baseURL.replace(/\/+$/, '') + '/api'
const api = axios.create({ baseURL, timeout: 30000 })

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
