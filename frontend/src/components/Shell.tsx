import { useEffect, useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { LogOut, Menu, X, Search, ChevronLeft } from 'lucide-react'
import { useAuth } from '../store/auth'
import { Icon } from '../icons'
import api from '../api'
import type { Modulo } from '../types'

export function Shell() {
  const { usuario, modulos, sair } = useAuth()
  const [catalogo, setCatalogo] = useState<Modulo[]>([])
  const [aberto, setAberto] = useState(false) // mobile drawer
  const [recolhido, setRecolhido] = useState(false) // desktop collapse
  const loc = useLocation()
  const nav = useNavigate()

  useEffect(() => {
    api.get('/meta/modulos').then((r) => setCatalogo(r.data.modulos)).catch(() => {})
  }, [])

  if (!usuario) return <Outlet />

  const visiveis = catalogo.filter((m) => modulos.includes(m.key))
  const grupos = [...new Set(visiveis.map((m) => m.grupo))]
  const ativo = (key: string) => loc.pathname === (key === 'dashboard' ? '/' : `/${key}`)
  const href = (key: string) => (key === 'dashboard' ? '/' : `/${key}`)

  const principais = visiveis.slice(0, 4)

  const NavItem = ({ m }: { m: Modulo }) => (
    <Link
      to={href(m.key)} onClick={() => setAberto(false)}
      title={m.label}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all group relative ${
        ativo(m.key) ? 'bg-neutral-900 text-white shadow-sm' : 'text-neutral-600 hover:bg-neutral-100'
      } ${recolhido ? 'lg:justify-center' : ''}`}
    >
      <Icon name={m.icone} className="w-[18px] h-[18px] shrink-0" />
      {!recolhido && <span className="text-sm font-medium truncate">{m.label}</span>}
      {m.sensivel && !recolhido && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-500" title="Dado sensível" />}
    </Link>
  )

  return (
    <div className="min-h-screen bg-neutral-50 flex">
      {/* Sidebar desktop / drawer mobile */}
      {aberto && <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 lg:hidden" onClick={() => setAberto(false)} />}
      <aside className={`fixed lg:sticky top-0 z-50 h-screen bg-white border-r border-neutral-200 flex flex-col transition-all duration-300
        ${recolhido ? 'lg:w-[76px]' : 'lg:w-64'} w-64 ${aberto ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="h-16 flex items-center justify-between px-4 border-b border-neutral-100">
          {!recolhido && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-neutral-900 text-white grid place-items-center font-bold text-sm">T</div>
              <div className="leading-tight">
                <p className="font-bold text-sm tracking-tight">TRK OS</p>
                <p className="text-[10px] text-neutral-400 uppercase tracking-wider">Sistema do Grupo</p>
              </div>
            </div>
          )}
          {recolhido && <div className="w-8 h-8 mx-auto rounded-lg bg-neutral-900 text-white grid place-items-center font-bold text-sm">T</div>}
          <button onClick={() => setAberto(false)} className="lg:hidden p-1.5 text-neutral-400 hover:bg-neutral-100 rounded-lg"><X className="w-5 h-5" /></button>
          <button onClick={() => setRecolhido(!recolhido)} className="hidden lg:flex p-1.5 text-neutral-400 hover:bg-neutral-100 rounded-lg">
            <ChevronLeft className={`w-4 h-4 transition-transform ${recolhido && 'rotate-180'}`} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-4">
          {grupos.map((g) => (
            <div key={g}>
              {!recolhido && <p className="px-3 mb-1 text-[10px] font-bold text-neutral-400 uppercase tracking-wider">{g}</p>}
              <div className="space-y-1">
                {visiveis.filter((m) => m.grupo === g).map((m) => <NavItem key={m.key} m={m} />)}
              </div>
            </div>
          ))}
        </nav>

        <div className="p-3 border-t border-neutral-100">
          <button onClick={() => { sair(); nav('/login') }}
            className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-neutral-500 hover:bg-danger-50 hover:text-danger-600 transition ${recolhido ? 'lg:justify-center' : ''}`}>
            <LogOut className="w-[18px] h-[18px]" />{!recolhido && <span className="text-sm font-medium">Sair</span>}
          </button>
        </div>
      </aside>

      {/* Conteúdo */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white/80 backdrop-blur border-b border-neutral-200 sticky top-0 z-30 flex items-center gap-3 px-4 lg:px-6">
          <button onClick={() => setAberto(true)} className="lg:hidden p-2 -ml-2 text-neutral-600 hover:bg-neutral-100 rounded-lg"><Menu className="w-5 h-5" /></button>
          <div className="hidden md:flex items-center gap-2 flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
              <input placeholder="Buscar no TRK OS…" className="w-full pl-9 pr-3 h-9 text-sm bg-neutral-100 border border-transparent rounded-xl focus:bg-white focus:border-neutral-300 focus:outline-none transition" />
            </div>
          </div>
          <div className="flex items-center gap-3 ml-auto">
            <div className="text-right hidden sm:block leading-tight">
              <p className="text-sm font-semibold">{usuario.nome}</p>
              <p className="text-xs text-neutral-500">{usuario.departamento_nome ?? usuario.cargo}</p>
            </div>
            <div className="w-9 h-9 rounded-full grid place-items-center text-white font-semibold text-sm" style={{ background: usuario.avatar_cor }}>
              {usuario.nome.charAt(0).toUpperCase()}
            </div>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-7 pb-24 lg:pb-7 max-w-[1400px] w-full mx-auto">
          <div className="animate-fade-in"><Outlet /></div>
        </main>
      </div>

      {/* Bottom nav mobile */}
      <nav className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur border-t border-neutral-200 flex" style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
        {principais.map((m) => (
          <Link key={m.key} to={href(m.key)} className={`flex-1 flex flex-col items-center gap-0.5 py-2 text-[11px] font-medium ${ativo(m.key) ? 'text-neutral-900' : 'text-neutral-400'}`}>
            <Icon name={m.icone} className="w-5 h-5" />{m.label.split(' ')[0]}
          </Link>
        ))}
        <button onClick={() => setAberto(true)} className="flex-1 flex flex-col items-center gap-0.5 py-2 text-[11px] font-medium text-neutral-400">
          <Menu className="w-5 h-5" />Mais
        </button>
      </nav>
    </div>
  )
}
