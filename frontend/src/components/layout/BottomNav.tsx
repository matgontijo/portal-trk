// frontend/src/components/layout/BottomNav.tsx
// Barra de navegação inferior — só no mobile (lg:hidden).
// Padrão "app nativo": acesso com o polegar aos destinos principais.

import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, GitBranch, CheckSquare, KanbanSquare, MoreHorizontal } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'

const ITEMS = [
  { label: 'Início', path: '/', icon: LayoutDashboard, roles: ['admin', 'gestor', 'funcionario'] },
  { label: 'Pipes', path: '/pipes', icon: GitBranch, roles: ['admin', 'gestor', 'funcionario'] },
  { label: 'Rotinas', path: '/rotinas', icon: CheckSquare, roles: ['admin', 'gestor', 'funcionario'] },
  { label: 'Tarefas', path: '/tarefas', icon: KanbanSquare, roles: ['admin', 'gestor', 'funcionario'] },
]

export function BottomNav() {
  const { user } = useAuthStore()
  const { setMobileNavVisible } = useUIStore()
  const location = useLocation()
  if (!user) return null

  const visiveis = ITEMS.filter((i) => i.roles.includes(user.role))

  const isActive = (path: string) =>
    location.pathname === path || (path !== '/' && location.pathname.startsWith(path))

  return (
    <nav
      className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur border-t border-neutral-200 flex items-stretch"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      {visiveis.map((item) => {
        const ativo = isActive(item.path)
        return (
          <Link
            key={item.path}
            to={item.path}
            className={`flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[11px] font-medium transition-colors ${
              ativo ? 'text-neutral-900' : 'text-neutral-400'
            }`}
          >
            <item.icon className={`w-5 h-5 ${ativo ? 'scale-110' : ''} transition-transform`} />
            {item.label}
          </Link>
        )
      })}
      <button
        onClick={() => setMobileNavVisible(true)}
        className="flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[11px] font-medium text-neutral-400 hover:text-neutral-900 transition-colors"
      >
        <MoreHorizontal className="w-5 h-5" />
        Mais
      </button>
    </nav>
  )
}
