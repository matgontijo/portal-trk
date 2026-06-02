// frontend/src/pages/Login.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogIn, AlertCircle, Eye, EyeOff } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import logoTrk from '../assets/logo-trk.svg'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  
  const login = useAuthStore((state) => state.login)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao realizar login')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      {/* Fundo com gradiente sutil */}
      <div className="login-bg" />
      
      <div className="login-container">
        {/* Card de Login */}
        <div className="login-card">
          {/* Logo */}
          <div className="login-logo-wrapper">
            <img src={logoTrk} alt="TRK Imóveis" className="login-logo" />
          </div>
          
          <div className="login-divider" />
          
          <p className="login-subtitle">
            Portal Operacional
          </p>

          <form className="login-form" onSubmit={handleSubmit}>
            {error && (
              <div className="login-error">
                <AlertCircle className="login-error-icon" />
                <span>{error}</span>
              </div>
            )}

            <div className="login-field">
              <label className="login-label" htmlFor="login-email">
                E-mail
              </label>
              <input
                id="login-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="login-input"
                placeholder="seu@email.com"
                autoComplete="email"
              />
            </div>

            <div className="login-field">
              <div className="login-label-row">
                <label className="login-label" htmlFor="login-password">
                  Senha
                </label>
                <a href="#" className="login-forgot">
                  Esqueceu?
                </a>
              </div>
              <div className="login-password-wrapper">
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="login-input"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="login-eye-btn"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="login-submit"
            >
              {isLoading ? (
                <div className="login-spinner" />
              ) : (
                <>
                  <LogIn size={18} />
                  Entrar
                </>
              )}
            </button>
          </form>

          <p className="login-footer">
            Sistema restrito a colaboradores autorizados
          </p>
        </div>
      </div>
    </div>
  )
}
