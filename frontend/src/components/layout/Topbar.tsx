// frontend/src/components/layout/Topbar.tsx
import { Menu, Search } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'
import { NotificationsBell } from './NotificationsBell'

export function Topbar() {
  const { user } = useAuthStore()
  const { setMobileNavVisible } = useUIStore()

  return (
    <header className="h-16 bg-white border-b border-neutral-200 flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30 transition-colors">
      
      {/* Left side: Mobile menu & Global Search */}
      <div className="flex items-center gap-4 flex-1">
        <button 
          onClick={() => setMobileNavVisible(true)}
          className="lg:hidden p-2 -ml-2 text-neutral-600 hover:bg-neutral-100 rounded-lg"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden md:flex relative w-96 max-w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
          <input 
            type="text" 
            placeholder="Buscar empresas, rotinas ou tarefas..." 
            className="w-full pl-9 pr-16 h-9 text-sm bg-neutral-50 border border-transparent text-neutral-900 placeholder:text-neutral-400 rounded-full focus:border-neutral-300 focus:bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900/5 transition-all"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <kbd className="text-[10px] font-sans px-1.5 py-0.5 rounded border border-neutral-200 bg-white text-neutral-400">Ctrl</kbd>
            <kbd className="text-[10px] font-sans px-1.5 py-0.5 rounded border border-neutral-200 bg-white text-neutral-400">K</kbd>
          </div>
        </div>
      </div>

      {/* Right side: Actions & User */}
      <div className="flex items-center gap-3">
        <NotificationsBell />

        <div className="h-6 w-px bg-neutral-200 mx-1"></div>

        <div className="flex items-center gap-3 pl-1">
          <div className="flex flex-col items-end hidden sm:flex">
            <span className="text-sm font-medium text-neutral-900 leading-tight">{user?.name}</span>
            <span className="text-xs text-neutral-500 capitalize">{user?.role}</span>
          </div>
          <div className="w-8 h-8 rounded-full bg-neutral-900 text-white flex items-center justify-center font-medium text-sm">
            {user?.name.charAt(0).toUpperCase()}
          </div>
        </div>
      </div>
    </header>
  )
}
