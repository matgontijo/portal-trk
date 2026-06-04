// frontend/src/components/layout/NotificationsBell.tsx
// Sino de notificações funcional: badge de não-lidas + dropdown + marcar lidas.

import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, AlertTriangle, CheckCircle2, ListTodo, FileText, Info, CheckCheck } from 'lucide-react'
import api from '../../services/api'

interface Notificacao {
  id: string
  tipo: string
  titulo: string
  mensagem: string | null
  link_acao: string | null
  lida: boolean
  created_at: string
}

const ICONE: Record<string, { Icon: typeof Bell; cls: string }> = {
  divergencia: { Icon: AlertTriangle, cls: 'text-danger-600 bg-danger-50' },
  sync_concluido: { Icon: CheckCircle2, cls: 'text-success-600 bg-success-50' },
  tarefa_atribuida: { Icon: ListTodo, cls: 'text-neutral-700 bg-neutral-100' },
  relatorio_disponivel: { Icon: FileText, cls: 'text-neutral-700 bg-neutral-100' },
  sistema: { Icon: Info, cls: 'text-warning-600 bg-warning-50' },
}

function tempoRelativo(iso: string): string {
  const min = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (min < 1) return 'agora'
  if (min < 60) return `${min} min`
  const h = Math.floor(min / 60)
  if (h < 24) return `${h}h`
  return `${Math.floor(h / 24)}d`
}

export function NotificationsBell() {
  const [count, setCount] = useState(0)
  const [aberto, setAberto] = useState(false)
  const [items, setItems] = useState<Notificacao[]>([])
  const [carregando, setCarregando] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  const buscarCount = useCallback(async () => {
    try { setCount((await api.get<{ count: number }>('/notificacoes/count')).data.count) }
    catch { /* silencioso */ }
  }, [])

  useEffect(() => {
    buscarCount()
    const t = setInterval(buscarCount, 30000)
    return () => clearInterval(t)
  }, [buscarCount])

  useEffect(() => {
    const fora = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setAberto(false) }
    document.addEventListener('mousedown', fora)
    return () => document.removeEventListener('mousedown', fora)
  }, [])

  const abrir = async () => {
    const novo = !aberto
    setAberto(novo)
    if (novo) {
      setCarregando(true)
      try { setItems((await api.get<Notificacao[]>('/notificacoes')).data) }
      catch { /* silencioso */ } finally { setCarregando(false) }
    }
  }

  const marcarTodas = async () => {
    await api.patch('/notificacoes/marcar-lida', { todas: true })
    setItems((p) => p.map((n) => ({ ...n, lida: true })))
    setCount(0)
  }

  const clicar = async (n: Notificacao) => {
    if (!n.lida) {
      await api.patch('/notificacoes/marcar-lida', { ids: [n.id] })
      setCount((c) => Math.max(0, c - 1))
    }
    setAberto(false)
    if (n.link_acao) navigate(n.link_acao)
  }

  return (
    <div className="relative" ref={ref}>
      <button onClick={abrir} className="p-2 text-neutral-500 hover:bg-neutral-100 rounded-full transition-colors relative" aria-label="Notificações">
        <Bell className="w-5 h-5" />
        {count > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center ring-2 ring-white">
            {count > 9 ? '9+' : count}
          </span>
        )}
      </button>

      {aberto && (
        <div className="fixed sm:absolute inset-x-2 sm:inset-x-auto sm:right-0 top-16 sm:top-auto sm:mt-2 sm:w-96 bg-white rounded-xl shadow-modal border border-neutral-200 z-50 max-h-[70vh] flex flex-col animate-scale-in">
          <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-100">
            <h3 className="font-semibold text-sm">Notificações</h3>
            {count > 0 && (
              <button onClick={marcarTodas} className="text-xs text-neutral-500 hover:text-neutral-900 flex items-center gap-1">
                <CheckCheck className="w-3.5 h-3.5" /> Marcar todas
              </button>
            )}
          </div>

          <div className="overflow-y-auto">
            {carregando ? (
              <div className="p-6 text-center text-sm text-neutral-400">Carregando…</div>
            ) : items.length === 0 ? (
              <div className="p-8 text-center text-sm text-neutral-400">
                <Bell className="w-8 h-8 mx-auto mb-2 text-neutral-200" />
                Nenhuma notificação.
              </div>
            ) : (
              items.map((n) => {
                const meta = ICONE[n.tipo] ?? ICONE.sistema
                const Icon = meta.Icon
                return (
                  <button key={n.id} onClick={() => clicar(n)}
                    className={`w-full text-left flex gap-3 px-4 py-3 hover:bg-neutral-50 transition-colors border-b border-neutral-50 ${!n.lida ? 'bg-neutral-50/60' : ''}`}>
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${meta.cls}`}>
                      <Icon className="w-4 h-4" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="flex items-center justify-between gap-2">
                        <span className={`text-sm truncate ${!n.lida ? 'font-semibold' : 'font-medium'}`}>{n.titulo}</span>
                        <span className="text-[11px] text-neutral-400 shrink-0">{tempoRelativo(n.created_at)}</span>
                      </span>
                      {n.mensagem && <span className="block text-xs text-neutral-500 line-clamp-2 mt-0.5">{n.mensagem}</span>}
                    </span>
                    {!n.lida && <span className="w-2 h-2 rounded-full bg-red-500 shrink-0 mt-1.5" />}
                  </button>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}
