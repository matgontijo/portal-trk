// frontend/src/components/layout/Sidebar.tsx
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  ArrowRightLeft, 
  CheckSquare, 
  KanbanSquare,
  GitBranch,
  Building2,
  Settings,
  Zap,
  LogOut,
  ChevronLeft
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'
import logoTrk from '../../assets/logo-trk.svg'

export function Sidebar() {
  const { user, logout } = useAuthStore()
  const { sidebarOpen, setSidebarOpen, mobileNavVisible, setMobileNavVisible } = useUIStore()
  const location = useLocation()

  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard, roles: ['admin', 'gestor', 'funcionario'] },
    { label: 'Conciliação', path: '/conciliacao', icon: ArrowRightLeft, roles: ['admin', 'gestor', 'funcionario'] },
    { label: 'Rotinas', path: '/rotinas', icon: CheckSquare, roles: ['admin', 'gestor', 'funcionario'] },
    { label: 'Tarefas', path: '/tarefas', icon: KanbanSquare, roles: ['admin', 'gestor', 'funcionario'] },
    { label: 'Pipes', path: '/pipes', icon: GitBranch, roles: ['admin', 'gestor', 'funcionario'] },
    { label: 'Automações', path: '/automacoes', icon: Zap, roles: ['admin', 'gestor'] },
    { label: 'Empresas', path: '/empresas', icon: Building2, roles: ['admin', 'gestor'] },
    { label: 'Usuários', path: '/usuarios', icon: Settings, roles: ['admin', 'gestor'] },
    { label: 'Configurações', path: '/config', icon: Settings, roles: ['admin'] },
  ]

  const visibleItems = navItems.filter(item => user && item.roles.includes(user.role))

  return (
    <>
      {/* Mobile Overlay */}
      {mobileNavVisible && (
        <div 
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileNavVisible(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-screen bg-white
        border-r border-neutral-200
        transition-all duration-300 flex flex-col
        ${sidebarOpen ? 'w-64' : 'w-20'}
        ${mobileNavVisible ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Header com Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-neutral-200">
          {sidebarOpen ? (
            <img src={logoTrk} alt="TRK" className="h-8 w-auto" style={{ color: '#1a1a1a' }} />
          ) : (
            <span className="font-light text-xl text-neutral-900 mx-auto tracking-widest">TRK</span>
          )}
          
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden lg:flex p-1.5 rounded-lg text-neutral-400 hover:bg-neutral-100 hover:text-neutral-700 transition-colors"
          >
            <ChevronLeft className={`w-5 h-5 transition-transform ${!sidebarOpen && 'rotate-180'}`} />
          </button>
        </div>

        {/* Nav Links */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {visibleItems.map((item) => {
            const isActive = location.pathname === item.path || 
                             (item.path !== '/' && location.pathname.startsWith(item.path))
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center px-3 py-2.5 rounded-lg transition-all duration-150 group relative
                  ${isActive 
                    ? 'bg-neutral-900 text-white font-medium shadow-sm' 
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'}
                  ${!sidebarOpen && 'justify-center'}
                `}
                onClick={() => setMobileNavVisible(false)}
              >
                <item.icon className={`w-5 h-5 flex-shrink-0 ${sidebarOpen ? 'mr-3' : ''}`} />
                {sidebarOpen && <span className="text-sm">{item.label}</span>}
                
                {/* Tooltip for collapsed state */}
                {!sidebarOpen && (
                  <div className="absolute left-full ml-2 px-2.5 py-1.5 bg-neutral-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible whitespace-nowrap z-50 shadow-lg">
                    {item.label}
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer (User & Logout) */}
        <div className="p-4 border-t border-neutral-200">
          {sidebarOpen && user && (
            <div className="flex items-center gap-3 mb-3 px-2">
              <div className="w-8 h-8 rounded-full bg-neutral-900 text-white flex items-center justify-center font-medium text-sm">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-900 truncate">{user.name}</p>
                <p className="text-xs text-neutral-500 capitalize">{user.role}</p>
              </div>
            </div>
          )}
          <button
            onClick={logout}
            className={`
              flex items-center w-full px-3 py-2 rounded-lg text-neutral-500
              hover:bg-red-50 hover:text-red-600 transition-colors
              ${!sidebarOpen && 'justify-center'}
            `}
          >
            <LogOut className={`w-5 h-5 ${sidebarOpen ? 'mr-3' : ''}`} />
            {sidebarOpen && <span className="text-sm">Sair</span>}
          </button>
        </div>
      </aside>
    </>
  )
}
