import { useEffect, useState, useCallback } from 'react'
import { Check, CalendarCheck, Repeat } from 'lucide-react'
import api from '../api'

interface Bloco { id: string; tipo: string; label: string; is_done: boolean; valor_texto?: string | null }
interface Rotina { id: string; nome: string; recorrencia_texto: string; categoria: string; blocos: Bloco[]; total: number; feitos: number }

export function Rotinas() {
  const [rotinas, setRotinas] = useState<Rotina[]>([])
  const [loading, setLoading] = useState(true)

  const carregar = useCallback(async () => {
    try { setRotinas((await api.get('/rotinas/hoje')).data) } finally { setLoading(false) }
  }, [])
  useEffect(() => { carregar() }, [carregar])

  const toggle = async (r: Rotina, b: Bloco) => {
    await api.put('/rotinas/progresso', { rotina_id: r.id, bloco_id: b.id, is_done: !b.is_done })
    carregar()
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Rotinas de Hoje</h1>
        <p className="text-neutral-500 mt-1">Seu checklist do dia. Marque conforme conclui.</p>
      </div>

      {loading ? (
        <div className="space-y-3">{[1, 2].map((i) => <div key={i} className="skeleton h-40" />)}</div>
      ) : rotinas.length === 0 ? (
        <div className="card p-10 text-center text-neutral-500">
          <CalendarCheck className="w-10 h-10 mx-auto mb-3 text-neutral-300" />
          Nenhuma rotina para hoje. Aproveite! (ou instale uma em <strong>Skills</strong>)
        </div>
      ) : (
        <div className="grid lg:grid-cols-2 gap-4">
          {rotinas.map((r) => {
            const pct = r.total ? Math.round((r.feitos / r.total) * 100) : 0
            return (
              <div key={r.id} className="card p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{r.nome}</h3>
                    <p className="text-xs text-neutral-500 flex items-center gap-1 mt-0.5"><Repeat className="w-3 h-3" /> {r.recorrencia_texto}</p>
                  </div>
                  <span className="text-sm font-semibold text-neutral-500">{r.feitos}/{r.total}</span>
                </div>
                <div className="h-2 bg-neutral-100 rounded-full overflow-hidden mt-3">
                  <div className={`h-full rounded-full transition-all duration-700 ${pct === 100 ? 'bg-emerald-500' : 'bg-neutral-900'}`} style={{ width: `${pct}%` }} />
                </div>
                <div className="mt-4 space-y-1.5">
                  {r.blocos.filter((b) => b.tipo === 'checkbox' || b.tipo === 'text_long').map((b) => (
                    <button key={b.id} onClick={() => toggle(r, b)} className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-50 text-left transition">
                      <span className={`w-5 h-5 rounded-md border grid place-items-center shrink-0 transition ${b.is_done ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-neutral-300'}`}>
                        {b.is_done && <Check className="w-3.5 h-3.5" />}
                      </span>
                      <span className={`text-sm ${b.is_done ? 'line-through text-neutral-400' : ''}`}>{b.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
