// frontend/src/App.tsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppLayout } from './components/layout/AppLayout'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { Conciliacao } from './pages/Conciliacao'
import { Rotinas } from './pages/Rotinas'
import { Tarefas } from './pages/Tarefas'
import { Automacoes } from './pages/Automacoes'
import { Pipes } from './pages/Pipes'
import { PipeBoard } from './pages/PipeBoard'
import { Empresas } from './pages/Empresas'
import { Configuracoes } from './pages/Configuracoes'
import { Usuarios } from './pages/Usuarios'
import { RoleGuard } from './components/common/RoleGuard'
import { ToastProvider } from './components/common/Toast'

// React Query Client setup
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route element={<AppLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/conciliacao" element={<Conciliacao />} />
            <Route path="/rotinas" element={<Rotinas />} />
            <Route path="/tarefas" element={<Tarefas />} />
            <Route path="/pipes" element={<Pipes />} />
            <Route path="/pipes/:id" element={<PipeBoard />} />
            
            <Route path="/automacoes" element={
              <RoleGuard allowedRoles={['admin', 'gestor']}>
                <Automacoes />
              </RoleGuard>
            } />

            <Route path="/empresas" element={
              <RoleGuard allowedRoles={['admin', 'gestor']}>
                <Empresas />
              </RoleGuard>
            } />
            
            <Route path="/usuarios" element={
              <RoleGuard allowedRoles={['admin', 'gestor']}>
                <Usuarios />
              </RoleGuard>
            } />
            
            <Route path="/config" element={
              <RoleGuard allowedRoles={['admin']}>
                <Configuracoes />
              </RoleGuard>
            } />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
      </ToastProvider>
    </QueryClientProvider>
  )
}
