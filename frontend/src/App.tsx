import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './store/auth'
import { ToastProvider } from './components/Toast'
import { Shell } from './components/Shell'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { Usuarios } from './pages/Usuarios'
import { Departamentos } from './pages/Departamentos'
import { Saldos } from './pages/Saldos'
import { Tarefas } from './pages/Tarefas'
import { Rotinas } from './pages/Rotinas'
import { Pipes } from './pages/Pipes'
import { Automacoes } from './pages/Automacoes'
import { Skills } from './pages/Skills'
import { Empresas } from './pages/Empresas'
import { ModuloEmBreve } from './pages/ModuloEmBreve'

function Protegido({ modulo, children }: { modulo: string; children: React.ReactNode }) {
  const { usuario, pode, carregando } = useAuth()
  const loc = useLocation()
  if (carregando) return null
  if (!usuario) return <Navigate to="/login" state={{ from: loc }} replace />
  if (!pode(modulo)) return <Navigate to="/" replace />
  return <>{children}</>
}

const PAGINAS: Record<string, React.ReactNode> = {
  usuarios: <Usuarios />, departamentos: <Departamentos />, saldos: <Saldos />,
  tarefas: <Tarefas />, rotinas: <Rotinas />, pipes: <Pipes />,
  automacoes: <Automacoes />, skills: <Skills />, empresas: <Empresas />,
}
const EM_BREVE = ['conciliacao', 'contas_bancarias', 'rh', 'comercial', 'relatorios', 'configuracoes']

export default function App() {
  const { carregar, carregando, usuario } = useAuth()
  useEffect(() => { carregar() }, [carregar])

  if (carregando) {
    return <div className="min-h-screen grid place-items-center bg-neutral-50"><div className="w-10 h-10 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin" /></div>
  }

  return (
    <ToastProvider>
      <Routes>
        <Route path="/login" element={usuario ? <Navigate to="/" replace /> : <Login />} />
        <Route element={<Shell />}>
          <Route path="/" element={<Protegido modulo="dashboard"><Dashboard /></Protegido>} />
          {Object.entries(PAGINAS).map(([m, el]) => (
            <Route key={m} path={`/${m}`} element={<Protegido modulo={m}>{el}</Protegido>} />
          ))}
          {EM_BREVE.map((m) => (
            <Route key={m} path={`/${m}`} element={<Protegido modulo={m}><ModuloEmBreve modulo={m} /></Protegido>} />
          ))}
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ToastProvider>
  )
}
